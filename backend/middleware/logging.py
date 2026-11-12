
import json
import logging
import time
import uuid
import traceback

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger("tripcs.access")


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "event": getattr(
                record,
                "event",
                "http_request",
            ),
            "request_id": getattr(
                record,
                "request_id",
                None,
            ),
            "method": getattr(record, "method", None),
            "path": getattr(record, "path", None),
            "status_code": getattr(
                record,
                "status_code",
                None,
            ),
            "duration_ms": getattr(
                record,
                "duration_ms",
                None,
            ),
        }

        if record.exc_info:
            log_data["error_type"] = (
                record.exc_info[0].__name__
            )
            log_data["traceback"] = "".join(
                traceback.format_exception(
                    *record.exc_info
                )
            )

        return json.dumps(
            log_data,
            ensure_ascii=False,
        )


def configure_logging() -> None:
    if logger.handlers:
        return

    handler = logging.StreamHandler()
    handler.setFormatter(JsonLogFormatter())

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = uuid.uuid4().hex
        start_time = time.perf_counter()

        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code

            response.headers["X-Request-ID"] = request_id

            return response

        except Exception:
            logger.exception(
                "Unhandled request error",
                extra={
                    "event": "http_error",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": 500,
                },
            )
            raise

        finally:
            duration_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2,
            )

            logger.info(
                "HTTP request completed",
                extra={
                    "event": "http_request",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                },
            )
