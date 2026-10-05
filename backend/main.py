from fastapi import FastAPI
from backend.database import engine
from backend.routers.user import router as users_router
from backend.routers.auth import router as auth_router
from backend.routers.trip import router as trips_router
from backend.routers.trip_day import router as trip_days_router
from backend.routers.schedule import router as schedules_router

app = FastAPI()
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(trips_router)
app.include_router(trip_days_router)
app.include_router(schedules_router)