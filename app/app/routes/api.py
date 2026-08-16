from fastapi import APIRouter
from ..services import cache

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

@router.get("/dht11")
async def getDHT11_telemetry():
    return {
        "status" : "success",
        "data": cache.get_cache_dht11_data()
    }
    
@router.get("/moisture")
async def getSoilMoisture():
    return {
        "status" : "successs",
        "data" : cache.get_cache_soil_moisture()
    }