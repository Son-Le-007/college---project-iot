import json
import time
from .cache import set_sensor_cache

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

        if (current_time - last_saved_time) < TELEMETRY_PERSISTENCE_INTERVAL_TIME:
                return
            
        insert_telemetry(data)
        last_saved_time = current_time
        print("💾 [Services] Telemetry persistence interval met and saved.")

    except Exception as e:
        print(f"❌ [Services] Insert failed: {e}")