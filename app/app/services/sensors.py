import json
import time
from app.services.cache import set_sensor_cache, get_device_active
from app.services.ai_inference import predict_moisture_loss_rate, predict_mold_risk

from app.database import (
    insert_telemetry,
    get_24h_telemetry_summary_sync,
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

        # Live Feature Engineering and Mold Prediction
        features_24h = get_24h_telemetry_summary_sync(temp, hum, light, moist)
        mold_pred = predict_mold_risk(features_24h)
        data["mold_risk_code"] = mold_pred["risk_code"]
        data["mold_risk_label"] = mold_pred["risk_label"]

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