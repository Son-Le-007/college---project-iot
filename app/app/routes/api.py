from fastapi import APIRouter
from ..services import cache
from ..mqtt import send_mqtt_threhold

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
