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
        "is_motion": payload.get("isMotion"),
    }

    print(f"☁️ [Database] Attempting cloud insert: {row}")
    return supabase.table("telemetry").insert(row).execute()

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