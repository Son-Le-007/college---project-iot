import asyncio
from datetime import datetime, timedelta, timezone
from app.database import supabase

async def telemetry_cleanup_worker():
    while True:
        try:
            cutoff_time = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
            supabase.table("telemetry").delete().lt("created_at", cutoff_time).execute()
            print(f"🧹 [Worker] Pruned telemetry older than: {cutoff_time}")
        except Exception as e:
            print(f"❌ [Worker] Cleanup failed: {str(e)}")
            
        await asyncio.sleep(3600)