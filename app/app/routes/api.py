from fastapi import APIRouter, Query
from datetime import datetime, timedelta, timezone
from ..services import cache
from ..mqtt import send_mqtt_threhold
from fastapi import Form, HTTPException
from fastapi.responses import RedirectResponse
from app.database import get_db
from app.core.security import verify_password, create_access_token, hash_password
from ..database import supabase

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
async def login_api(email: str = Form(...), password: str = Form(...)):
    db = get_db()
    res = db.table("users").select("*").eq("email", email).execute()
    
    if not res.data:
        raise HTTPException(status_code=400, detail="Email không tồn tại")

    user = res.data[0]
    if not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Sai Mật Khẩu")

    token = create_access_token({"sub": user["email"]})
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response

@router.post("/register")
async def register_api(email: str = Form(...), password: str = Form(...)):
    db = get_db()
    res = db.table("users").select("*").eq("email", email).execute()
    
    if res.data:
        raise HTTPException(status_code=400, detail="Email đã tồn tại")
        
    db.table("users").insert({
        "email": email, 
        "password_hash": hash_password(password)
    }).execute()
    
    return RedirectResponse(url="/login", status_code=302)

@router.get("/logout")
async def logout_api():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response

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

async def _get_latest_persisted_metric(column_name: str):
    try:
        response = (
            supabase.table("telemetry")
            .select(column_name)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if response.data and len(response.data) > 0:
            val = response.data[0].get(column_name)
            if val is not None:
                return [{"value": val}]
        return []
    except Exception as e:
        print(f"❌ [API] Error fetching latest {column_name}: {e}")
        return []

async def _get_persisted_metric(column_name: str, window: int):
    try:
        cutoff_time = (datetime.now(timezone.utc) - timedelta(seconds=window)).isoformat()
        response = (
            supabase.table("telemetry")
            .select(f"created_at, {column_name}")
            .gte("created_at", cutoff_time)
            .order("created_at", desc=False)
            .execute()
        )
        return [
            {"timestamp": row.get("created_at"), "value": row.get(column_name)}
            for row in response.data or []
            if row.get(column_name) is not None
        ]
    except Exception as e:
        print(f"❌ [API] Error fetching {column_name}: {e}")
        return []