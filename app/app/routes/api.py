from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
import asyncio
import json
from ..services import cache
from ..database import supabase, _get_persisted_metric, _get_latest_persisted_metric

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

