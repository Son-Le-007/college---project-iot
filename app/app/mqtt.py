import os
import ssl
from pathlib import Path
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from app.services import sensors

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

MQTT_HOST = os.getenv("MQTT_HOST", "127.0.0.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

TOPIC_ROUTER = {
    "sensors": sensors.handle_sensor_telemetry,
}

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("✅ [MQTT] Connected successfully to MQTT !")
        for topic in TOPIC_ROUTER.keys():
            client.subscribe(topic)
            print(f"📡 [MQTT] Subscribed to: {topic}")
    else:
        print(f"❌ [MQTT] Connection failed with code: {reason_code}")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    
    print(f"📩 [MQTT] Incoming on {topic}")
    
    # Check if we have a service function ready for this topic
    if topic in TOPIC_ROUTER:
        TOPIC_ROUTER[topic](payload)  # Execute the service function dynamically!
    else:
        print(f"⚠️ [MQTT] No service handler registered for topic: {topic}")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

def start_mqtt():
    try:
        print("🔄 [MQTT] Connecting to Mosquitto container...")
        mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
        mqtt_client.loop_start()
    except Exception as e:
        print(f"❌ [MQTT] Initialization error: {str(e)}")