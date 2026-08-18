from fastapi import APIRouter, Query
from datetime import datetime, timedelta, timezone
from ..services import cache
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