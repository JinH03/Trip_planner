
import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.cache import get_redis_client
from backend.database import engine


router = APIRouter(
    prefix="/health",
    tags=["health"],
)

logger = logging.getLogger(__name__)


@router.get("/live")
def liveness_check():
    return {
        "status": "ok",
    }


@router.get("/ready")
def readiness_check():
    database_status = "up"
    redis_status = "up"

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    except SQLAlchemyError:
        database_status = "down"
        logger.warning("Health check: database unavailable")

    try:
        redis_client = get_redis_client()
        redis_client.ping()

    except Exception:
        redis_status = "down"
        logger.warning("Health check: Redis unavailable")

    is_ready = (
        database_status == "up"
        and redis_status == "up"
    )

    response_data = {
        "status": "ok" if is_ready else "degraded",
        "services": {
            "database": database_status,
            "redis": redis_status,
        },
    }

    return JSONResponse(
        status_code=200 if is_ready else 503,
        content=response_data,
    )
