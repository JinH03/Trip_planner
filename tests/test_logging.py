
import json
import logging

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from backend.middleware.logging import (
    JsonLogFormatter,
    RequestLoggingMiddleware,
    logger,
)


def create_test_app():
    test_app = FastAPI()
    test_app.add_middleware(RequestLoggingMiddleware)

    @test_app.get("/ok")
    def ok():
        return {"message": "success"}

    @test_app.get("/blocked")
    def blocked():
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
        )

    @test_app.get("/error")
    def error():
        raise ValueError("Test server error")

    return test_app


# 1. 정상 응답에 Request ID가 포함되는지 확인
def test_request_id_header():
    test_app = create_test_app()

    with TestClient(test_app) as client:
        response = client.get("/ok")

    assert response.status_code == 200

    request_id = response.headers["X-Request-ID"]
    assert len(request_id) == 32


# 2. 요청마다 서로 다른 Request ID를 생성하는지 확인
def test_request_id_is_unique():
    test_app = create_test_app()

    with TestClient(test_app) as client:
        response1 = client.get("/ok")
        response2 = client.get("/ok")

    assert (
        response1.headers["X-Request-ID"]
        != response2.headers["X-Request-ID"]
    )


# 3. HTTP 429 응답에도 Request ID가 포함되는지 확인
def test_request_id_on_429():
    test_app = create_test_app()

    with TestClient(test_app) as client:
        response = client.get("/blocked")

    assert response.status_code == 429
    assert "X-Request-ID" in response.headers


# 4. JSON 로그 형식 확인
def test_json_log_formatter():
    formatter = JsonLogFormatter()

    record = logging.LogRecord(
        name="tripcs.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Test request",
        args=(),
        exc_info=None,
    )

    record.event = "http_request"
    record.request_id = "test123"
    record.method = "GET"
    record.path = "/places/search"
    record.status_code = 200
    record.duration_ms = 12.5

    result = json.loads(formatter.format(record))

    assert result["event"] == "http_request"
    assert result["request_id"] == "test123"
    assert result["method"] == "GET"
    assert result["path"] == "/places/search"
    assert result["status_code"] == 200
    assert result["duration_ms"] == 12.5


# 5. 서버 예외 발생 시 에러 로그를 남기는지 확인
def test_server_error_logging():
    test_app = create_test_app()

    records = []

    class CaptureHandler(logging.Handler):
        def emit(self, record):
            records.append(record)

    handler = CaptureHandler()
    logger.addHandler(handler)

    try:
        with TestClient(
            test_app,
            raise_server_exceptions=False,
        ) as client:
            response = client.get("/error")

        assert response.status_code == 500

        error_logs = [
            record
            for record in records
            if getattr(record, "event", None) == "http_error"
        ]

        assert len(error_logs) == 1
        assert error_logs[0].status_code == 500
        assert error_logs[0].exc_info is not None

        formatter = JsonLogFormatter()
        log_data = json.loads(
            formatter.format(error_logs[0])
        )

        assert log_data["error_type"] == "ValueError"
        assert "traceback" in log_data

    finally:
        logger.removeHandler(handler)
