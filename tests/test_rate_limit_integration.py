
import time
from uuid import uuid4
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from redis.exceptions import RedisError

from backend.cache import get_redis_client
from backend.dependencies.rate_limit import (
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_SCRIPT,
    RATE_LIMIT_WINDOW_SECONDS,
)


def test_real_redis_rate_limit():
    redis_client = get_redis_client()

    try:
        redis_client.ping()
    except (RedisError, OSError):
        pytest.skip("Real Redis server is not available")

    # 기존 사용자의 Rate Limit 데이터와 충돌 방지
    key = f"tripcs:test:rate_limit:{uuid4().hex}"

    try:
        # 20회까지 허용
        for count in range(1, RATE_LIMIT_REQUESTS + 1):
            result = redis_client.eval(
                RATE_LIMIT_SCRIPT,
                1,
                key,
                RATE_LIMIT_WINDOW_SECONDS,
            )

            assert int(result[0]) == count

        # 21번째 요청은 제한을 초과해야 함
        result = redis_client.eval(
            RATE_LIMIT_SCRIPT,
            1,
            key,
            RATE_LIMIT_WINDOW_SECONDS,
        )

        assert int(result[0]) == RATE_LIMIT_REQUESTS + 1

        # TTL 확인
        ttl = redis_client.ttl(key)

        assert 0 < ttl <= RATE_LIMIT_WINDOW_SECONDS

    finally:
        redis_client.delete(key)
