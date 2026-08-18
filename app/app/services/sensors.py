import json
import time
from .cache import set_sensor_cache, get_device_active

from app.database import (
    insert_telemetry,
    TELEMETRY_PERSISTENCE_INTERVAL_TIME,
)

last_saved_time = 0


def handle_sensor_telemetry(payload: str):
    global last_saved_time

    current_time = time.time()

    try:
        data = json.loads(payload)

        set_sensor_cache(data)

        if not get_device_active():
            print("⚠️ [Services] Skip persistence: Device is marked INACTIVE.")
            return

        if (current_time - last_saved_time) < TELEMETRY_PERSISTENCE_INTERVAL_TIME:
                return
            
        insert_telemetry(data)
        last_saved_time = current_time
        print("✅ [Services] Telemetry successfully persisted to Supabase.")

    except Exception as e:
        print(f"❌ [Services] Insert failed: {e}")