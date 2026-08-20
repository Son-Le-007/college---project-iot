from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse
import asyncio
import json
from ..services import cache
from ..database import supabase, _get_persisted_metric, _get_latest_persisted_metric
from ..mqtt import send_mqtt_threhold
from fastapi import Form, HTTPException
from fastapi.responses import RedirectResponse
from app.database import get_db
from app.core.security import verify_password, create_access_token, hash_password
from app.mqtt import mqtt_client 

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

@router.get("/dht11")
async def getDHT11_telemetry():
    return {
        "status" : "success",
        "data": {
            "temperature": cache.get_cache_DHT_temperature(),
            "humidity": cache.get_cache_DHT_humidity(),
            "active": cache.get_device_active()
        }
    }
    
@router.get("/moisture")
async def getSoilMoisture():
    return {
        "status" : "success",
        "data" : {
            "soil_moisture": cache.get_cache_soil_moisture(),
            "active": cache.get_device_active()
        }
    }
    
@router.post("/threhold/save")
def setThreHold(data: dict):
    if "threshold" not in data:
        return {"status": "error", "message": "missing 'threshold' key"}
    try:
        threhold_val = float(data.get("threshold", 0))
    except:
        return {"status": "error", "message": "Invalid threshold number"}
    
    send_mqtt_threhold(threhold_val)
    return {"status" : "success"}



@router.post("/login")
async def login_api(request: Request, email: str = Form(...), password: str = Form(...)):
    db = get_db()
    res = db.table("users").select("*").eq("email", email).execute()
    
    if not res.data: 
        return request.app.state.templates.TemplateResponse(
            request=request, 
            name="login.html", 
            context={"request": request, "error": "Email này không tồn tại trong hệ thống!"}
        )
        
    user = res.data[0]
    if not verify_password(password, user["password_hash"]):
        return request.app.state.templates.TemplateResponse(
            request=request, 
            name="login.html", 
            context={"request": request, "error": "Sai mật khẩu, vui lòng thử lại!"}
        )
        
    token = create_access_token({"sub": user["email"]})
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response

@router.post("/register")
async def register_api(request: Request, email: str = Form(...), password: str = Form(...)):
    if len(password) < 6:
        return request.app.state.templates.TemplateResponse(
            request=request, 
            name="register.html", 
            context={"request": request, "error": "Mật khẩu quá yếu! Phải từ 6 ký tự trở lên."}
        )

    db = get_db()
    
    if db.table("users").select("*").eq("email", email).execute().data:
        return request.app.state.templates.TemplateResponse(
            request=request, 
            name="register.html", 
            context={"request": request, "error": "Email này đã có người đăng ký rồi!"}
        )
        
    db.table("users").insert({"email": email, "password_hash": hash_password(password)}).execute()
    return request.app.state.templates.TemplateResponse(
        request=request, 
        name="login.html", 
        context={"request": request, "success": "Đăng ký thành công! Hãy đăng nhập."}
    )

@router.get("/logout")
async def logout_api():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response

@router.post("/buzzer")
async def toggle_buzzer(data: dict):
    action = data.get("action")
    if action in ["ON", "OFF"]:
        mqtt_client.publish("garden/control/buzzer", json.dumps({"status": action}))
        return {"status": "success", "message": f"Còi đã {action}"}
    return {"status": "error"}


@router.get("/stream")
async def telemetry_stream():
    """SSE endpoint streaming real-time metrics and AI inferences."""
    async def event_generator():
        while True:
            payload = {
                "active": cache.get_device_active(),
                "temperature": cache.get_cache_DHT_temperature(),
                "humidity": cache.get_cache_DHT_humidity(),
                "soil_moisture": cache.get_cache_soil_moisture(),
                "ambient_light": cache.get_cache_ambient_light(), 
                "predicted_evaporation_speed": cache.get_cache_predicted_evaporation()
            }
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/metrics/persisted/chart/temperature")
async def get_persisted_temperature(window: int = Query(3600, description="Window in seconds")):
    return await _get_persisted_metric("temperature", window)

@router.get("/metrics/persisted/chart/humidity")
async def get_persisted_humidity(window: int = Query(3600, description="Window in seconds")):
    return await _get_persisted_metric("humidity", window)

@router.get("/metrics/persisted/chart/ambient_light")
async def get_persisted_ambient_light(window: int = Query(3600, description="Window in seconds")):
    return await _get_persisted_metric("ambient_light", window)

@router.get("/metrics/persisted/gauge/temperature")
async def get_latest_temperature():
    return await _get_latest_persisted_metric("temperature")

@router.get("/metrics/persisted/gauge/humidity")
async def get_latest_humidity():
    return await _get_latest_persisted_metric("humidity")

@router.get("/metrics/persisted/gauge/ambient_light")
async def get_latest_ambient_light():
    return await _get_latest_persisted_metric("ambient_light")

