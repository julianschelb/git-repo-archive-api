from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import Settings
from .routers import service
import datetime
from .routers.service import reclone_repos_internal

# =================== Settings ===================

# Load application settings
settings = Settings()

tags_metadata = [
    {
        "name": "service",
        "description": "Entity Linking",
    },
]
app = FastAPI(
    title=settings.app_name,
    version=settings.app_vesion,
    description=settings.app_description,
    contact={
        "name": settings.contact_name,
        "url": settings.contact_url,
        "email": settings.contact_email,
    },
    license_info={
        "name": settings.license_name,
        "url": settings.license_url,
    },
    openapi_tags=tags_metadata,
)

# CORS Settings
origins = [
    "http://localhost",
    "http://localhost:8081",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register sub modules
app.include_router(service.router, tags=["service"])


# =================== Scheduler ===================


scheduler = BackgroundScheduler()


@app.on_event("startup")
async def start_scheduler():
    scheduler.start()


@app.on_event("shutdown")
async def shutdown_scheduler():
    scheduler.shutdown()


# Schedule print_date_time to be called every 5 seconds
scheduler.add_job(
    func=service.reclone_repos_internal,
    trigger=IntervalTrigger(hours=6),  # TODO: move to config
    id='reclone_repos',
    name='Reclone all repos',
    replace_existing=True
)
