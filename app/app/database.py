import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timedelta, timezone

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TELEMETRY_PERSISTENCE_INTERVAL_TIME = int(os.getenv("TELEMETRY_PERSISTENCE_INTERVAL_TIME", 10))

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def init_db():
    try:
        supabase.table("telemetry").select("id").limit(1).execute()
        print("✅ [Database] Table 'telemetry' verified.")
    except Exception as e:
        print(f"⚠️ [Database] Connection check warning: {e}")

def get_db() -> Client:
    return supabase

def insert_telemetry(payload: dict):
    row = {
        "temperature": payload.get("temperature"),
        "humidity": payload.get("humidity"),
        "ambient_light": payload.get("ambient_light"),
        "soil_moisture": payload.get("soil_moisture"),
        "ismotion": bool(payload.get("isMotion", False)),
    }

    print(f"☁️ [Database] Attempting cloud insert: {row}")
    return supabase.table("telemetry").insert(row).execute()

def get_24h_telemetry_summary_sync(current_temp: float, current_hum: float, current_light: float, current_moist: float) -> dict:
    try:
        cutoff_time = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        response = (
            supabase.table("telemetry")
            .select("temperature, humidity, ambient_light, soil_moisture")
            .gte("created_at", cutoff_time)
            .execute()
        )
        data = response.data or []
        if not data:
            return {
                "avg_temp": current_temp,
                "avg_humidity": current_hum,
                "avg_ambient_light": current_light,
                "avg_soil_moisture": current_moist,
                "high_humidity_ratio": 1.0 if current_hum >= 80.0 else 0.0
            }
        
        total = len(data)
        sum_temp = sum(row.get("temperature") or current_temp for row in data)
        sum_hum = sum(row.get("humidity") or current_hum for row in data)
        sum_light = sum(row.get("ambient_light") or current_light for row in data)
        sum_moist = sum(row.get("soil_moisture") or current_moist for row in data)
        high_hum_count = sum(1 for row in data if (row.get("humidity") or current_hum) >= 80.0)

        return {
            "avg_temp": sum_temp / total,
            "avg_humidity": sum_hum / total,
            "avg_ambient_light": sum_light / total,
            "avg_soil_moisture": sum_moist / total,
            "high_humidity_ratio": high_hum_count / total
        }
    except Exception as e:
        print(f"❌ [Database] Error computing 24h summary: {e}")
        return {
            "avg_temp": current_temp,
            "avg_humidity": current_hum,
            "avg_ambient_light": current_light,
            "avg_soil_moisture": current_moist,
            "high_humidity_ratio": 1.0 if current_hum >= 80.0 else 0.0
        }

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