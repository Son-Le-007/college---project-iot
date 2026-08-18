import sys
import asyncio
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.database import get_db, init_db
from app.mqtt import start_mqtt
from app.background_workers.db_cleanup_worker import telemetry_cleanup_worker
from app.background_workers.device_status_worker import device_status_worker
from app.routes.pages import router as pages_router
from app.routes.api import router as api_router

def create_app() -> FastAPI:
    app = FastAPI(title="College IoT App")

    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
    app.state.templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

    @app.on_event("startup")
    async def startup_event():
        init_db()
        start_mqtt()
        asyncio.create_task(telemetry_cleanup_worker())
        asyncio.create_task(device_status_worker())

    @app.get("/healthcheck")
    async def health_check(db=Depends(get_db)):
        try:
            db.table("telemetry").select("id").limit(1).execute()
            return {"status": "healthy", "database": "connected"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    app.include_router(pages_router)
    app.include_router(api_router, prefix="/api")

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)