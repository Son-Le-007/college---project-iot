import asyncio
import os
import time
from app.services.cache import get_last_received_time, set_device_active

DEVICE_ACTIVE_THRESHOLD_SEC = int(os.getenv("DEVICE_ACTIVE_THRESHOLD_SEC", 15))

async def device_status_worker():
    while True:
        try:
            last_received = get_last_received_time()
            elapsed = time.time() - last_received
            
            if last_received > 0 and elapsed <= DEVICE_ACTIVE_THRESHOLD_SEC:
                set_device_active(True)
            else:
                set_device_active(False)
        except Exception as e:
            print(f"❌ [Worker] Device status check failed: {str(e)}")
            
        await asyncio.sleep(2)