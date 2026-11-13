
from fastapi import FastAPI

from backend.database import engine
from backend.middleware.logging import (
    RequestLoggingMiddleware,
    configure_logging,
)
from backend.routers.user import router as users_router
from backend.routers.auth import router as auth_router
from backend.routers.trip import router as trips_router
from backend.routers.trip_day import router as trip_days_router
from backend.routers.schedule import router as schedules_router
from backend.routers.place import router as places_router
from backend.routers.favorite import router as favorites_router
from backend.routers.health import router as health_router


configure_logging()

app = FastAPI()

app.add_middleware(RequestLoggingMiddleware)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(trips_router)
app.include_router(trip_days_router)
app.include_router(schedules_router)
app.include_router(places_router)
app.include_router(favorites_router)
app.include_router(health_router)
