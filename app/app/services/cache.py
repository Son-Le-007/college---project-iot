import threading
import time

_cache_lock = threading.Lock()
_in_memory_cache = {
    "temperature": 0.0,
    "humidity": 0.0,
    "soil_moisture": 0.0,
    "ambient_light": 0.0,
    "predicted_evaporation_speed": 0.0,
    "last_received_time": 0.0,
    "device_active": False,
}

def set_sensor_cache(data: dict):
    with _cache_lock:
        _in_memory_cache["temperature"] = data.get("temperature", 0.0)
        _in_memory_cache["humidity"] = data.get("humidity", 0.0)
        _in_memory_cache["soil_moisture"] = data.get("soil_moisture", 0.0)
        _in_memory_cache["ambient_light"] = data.get("ambient_light", 0.0)
        _in_memory_cache["predicted_evaporation_speed"] = data.get("predicted_evaporation_speed", 0.0)
        _in_memory_cache["last_received_time"] = time.time()
    
def get_sensor_cache() -> dict:
    with _cache_lock:
        return _in_memory_cache.copy()

def get_cache_dht11_data() -> dict:
    dht_keys = ("temperature", "humidity")
    return {_in_memory_cache.get(key, 0.0) for key in dht_keys}

def get_cache_DHT_temperature() -> float:
    return _in_memory_cache.get("temperature", 0.0)

def get_cache_DHT_humidity() -> float:
    return _in_memory_cache.get("humidity", 0.0)

def get_cache_soil_moisture() -> float:
    return _in_memory_cache.get("soil_moisture", 0.0)

def get_cache_predicted_evaporation() -> float:
    return _in_memory_cache.get("predicted_evaporation_speed", 0.0)

def get_last_received_time() -> float:
    with _cache_lock:
        return _in_memory_cache.get("last_received_time", 0.0)

def get_device_active() -> bool:
    with _cache_lock:
        return _in_memory_cache.get("device_active", False)

def set_device_active(active: bool):
    with _cache_lock:
        _in_memory_cache["device_active"] = active