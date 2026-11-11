
from fastapi import Depends, HTTPException, status
from redis.exceptions import RedisError

from backend.cache import get_redis_client
from backend.dependencies.auth import get_current_user
from backend.models import User


RATE_LIMIT_REQUESTS = 20
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_KEY_PREFIX = "tripcs:rate_limit:places"


# INCR + EXPIRE를 하나의 원자적 작업으로 실행
RATE_LIMIT_SCRIPT = """
local count = redis.call('INCR', KEYS[1])

if count == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end

local ttl = redis.call('TTL', KEYS[1])

return {count, ttl}
"""


def enforce_place_search_rate_limit(
    current_user: User = Depends(get_current_user),
) -> None:
    """
    사용자별 장소 검색 요청 제한.

    - 60초 동안 최대 20회
    - 초과하면 429 반환
    - Redis 장애 시 검색 허용
    """

    cache_key = (
        f"{RATE_LIMIT_KEY_PREFIX}:{current_user.id}"
    )

    try:
        redis_client = get_redis_client()

        count, ttl = redis_client.eval(
            RATE_LIMIT_SCRIPT,
            1,
            cache_key,
            RATE_LIMIT_WINDOW_SECONDS,
        )

    except (RedisError, OSError):
        # Redis 장애 시 검색 기능은 유지한다.
        return

    if int(count) > RATE_LIMIT_REQUESTS:
        retry_after = max(1, int(ttl))

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many place search requests",
            headers={
                "Retry-After": str(retry_after),
            },
        )
