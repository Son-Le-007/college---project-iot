import json
import time
from .cache import set_sensor_cache, get_device_active
from .ai_inference import predict_moisture_loss_rate

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

        # 1. Run AI Inference immediately
        temp = data.get("temperature", 0.0)
        hum = data.get("humidity", 0.0)
        moist = data.get("soil_moisture", 0.0)
        light = data.get("ambient_light", 0.0)
        
        pred = predict_moisture_loss_rate(temp, hum, moist, light)
        data["predicted_evaporation_speed"] = pred

        # 2. Cache result
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