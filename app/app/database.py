import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

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
    }

    print(f"☁️ [Database] Attempting cloud insert: {row}")
    return supabase.table("telemetry").insert(row).execute()