from fastapi import FastAPI
from backend.database import engine
from backend.routers.user import router as users_router
from backend.routers.auth import router as auth_router
from backend.routers.trip import router as trips_router
app = FastAPI()
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(trips_router)

