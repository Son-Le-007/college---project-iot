from fastapi import APIRouter
from ..services import cache
from ..mqtt import send_mqtt_threhold
from fastapi import Form, HTTPException
from fastapi.responses import RedirectResponse
from app.database import get_db
from app.core.security import verify_password, create_access_token, hash_password

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
            "humidity": cache.get_cache_DHT_humidity()
        }
    }
    
@router.get("/moisture")
async def getSoilMoisture():
    return {
        "status" : "success",
        "data" : {
            "soil_moisture": cache.get_cache_soil_moisture()
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