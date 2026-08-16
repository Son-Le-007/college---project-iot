import threading

_cache_lock = threading.Lock()
_in_memory_cache = {
    "temperature":0.0,
    "humidity": 0.0,
    "soil_moisture": 0.0,
}

def set_sensor_cache(data: dict):
    with _cache_lock:
        _in_memory_cache["temperature"] = data.get("temperature", 0.0)
        _in_memory_cache["humidity"] = data.get("humidity", 0.0)
        _in_memory_cache["soil_moisture"] = data.get("soil_moisture", 0.0)
    
def get_sensor_cache() -> dict:
    with _cache_lock:
        return _in_memory_cache.copy()

def get_cache_dht11_data() -> dict:
    dht_keys = ("temperature", "humidity")
    return {key: _in_memory_cache.get(key, 0.0) for key in dht_keys}

def get_cache_soil_moisture() -> dict:
    return  {"soil_moisture": _in_memory_cache.get("soil_moisture", 0.0)}