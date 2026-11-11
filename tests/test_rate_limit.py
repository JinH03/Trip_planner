
from collections import defaultdict
from unittest.mock import MagicMock, patch

from redis.exceptions import ConnectionError as RedisConnectionError

from backend.dependencies.rate_limit import (
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW_SECONDS,
    enforce_place_search_rate_limit,
)


SEARCH_URL = "/places/search"


def create_mock_rate_limit_client():
    client = MagicMock()
    client.eval.return_value = [1, 60]
    return client


# 1. 20회까지 정상 허용
def test_rate_limit_allows_20_requests(
    client,
    auth_headers,
):
    redis_client = create_mock_rate_limit_client()

    redis_client.eval.side_effect = [
        [count, 60]
        for count in range(1, 21)
    ]

    with (
        patch(
            "backend.dependencies.rate_limit.get_redis_client",
            return_value=redis_client,
        ),
        patch(
            "backend.routers.place.search_places_service",
            return_value=[],
        ) as mock_search,
    ):
        for _ in range(20):
            response = client.get(
                SEARCH_URL,
                headers=auth_headers,
                params={"query": "오사카성"},
            )

            assert response.status_code == 200

    assert redis_client.eval.call_count == 20
    assert mock_search.call_count == 20


# 2. 21번째 요청에서 429 반환
def test_rate_limit_blocks_21st_request(
    client,
    auth_headers,
):
    redis_client = create_mock_rate_limit_client()

    redis_client.eval.side_effect = [
        [count, 60]
        for count in range(1, 22)
    ]

    with (
        patch(
            "backend.dependencies.rate_limit.get_redis_client",
            return_value=redis_client,
        ),
        patch(
            "backend.routers.place.search_places_service",
            return_value=[],
        ) as mock_search,
    ):
        for _ in range(20):
            response = client.get(
                SEARCH_URL,
                headers=auth_headers,
                params={"query": "오사카성"},
            )
            assert response.status_code == 200

        response = client.get(
            SEARCH_URL,
            headers=auth_headers,
            params={"query": "오사카성"},
        )

    assert response.status_code == 429
    assert response.json()["detail"] == (
        "Too many place search requests"
    )

    # 차단된 요청은 장소 검색 함수까지 도달하지 않아야 한다.
    assert mock_search.call_count == 20


# 3. Retry-After 헤더 확인
def test_rate_limit_retry_after_header(
    client,
    auth_headers,
):
    redis_client = create_mock_rate_limit_client()
    redis_client.eval.return_value = [21, 45]

    with patch(
        "backend.dependencies.rate_limit.get_redis_client",
        return_value=redis_client,
    ):
        response = client.get(
            SEARCH_URL,
            headers=auth_headers,
            params={"query": "오사카성"},
        )

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "45"


# 4. 사용자별 카운터 분리
def test_rate_limit_isolated_by_user(
    client,
    auth_headers,
    second_auth_headers,
):
    redis_client = create_mock_rate_limit_client()

    counts = defaultdict(int)
    used_keys = []

    def fake_eval(script, numkeys, key, window):
        used_keys.append(key)
        counts[key] += 1
        return [counts[key], 60]

    redis_client.eval.side_effect = fake_eval

    with (
        patch(
            "backend.dependencies.rate_limit.get_redis_client",
            return_value=redis_client,
        ),
        patch(
            "backend.routers.place.search_places_service",
            return_value=[],
        ),
    ):
        # 사용자 A: 20회 검색
        for _ in range(20):
            response = client.get(
                SEARCH_URL,
                headers=auth_headers,
                params={"query": "오사카성"},
            )
            assert response.status_code == 200

        # 사용자 A: 21번째 검색 차단
        response_a = client.get(
            SEARCH_URL,
            headers=auth_headers,
            params={"query": "오사카성"},
        )

        # 사용자 B: 첫 번째 검색은 허용
        response_b = client.get(
            SEARCH_URL,
            headers=second_auth_headers,
            params={"query": "오사카성"},
        )

    assert response_a.status_code == 429
    assert response_b.status_code == 200

    # 서로 다른 사용자는 서로 다른 Redis Key를 사용
    assert len(set(used_keys)) == 2


# 5. TTL 만료 후 다시 허용
def test_rate_limit_resets_after_ttl(
    client,
    auth_headers,
):
    redis_client = create_mock_rate_limit_client()

    # 첫 번째 요청: 이미 제한을 초과한 상태
    # 두 번째 요청: TTL 만료 후 새 카운터 시작
    redis_client.eval.side_effect = [
        [21, 5],
        [1, 60],
    ]

    with (
        patch(
            "backend.dependencies.rate_limit.get_redis_client",
            return_value=redis_client,
        ),
        patch(
            "backend.routers.place.search_places_service",
            return_value=[],
        ),
    ):
        first_response = client.get(
            SEARCH_URL,
            headers=auth_headers,
            params={"query": "오사카성"},
        )

        second_response = client.get(
            SEARCH_URL,
            headers=auth_headers,
            params={"query": "오사카성"},
        )

    assert first_response.status_code == 429
    assert second_response.status_code == 200


# 6. Redis 장애 발생 시 검색 허용
def test_rate_limit_redis_failure_allows_search(
    client,
    auth_headers,
):
    redis_client = create_mock_rate_limit_client()

    redis_client.eval.side_effect = RedisConnectionError(
        "Redis connection failed"
    )

    with (
        patch(
            "backend.dependencies.rate_limit.get_redis_client",
            return_value=redis_client,
        ),
        patch(
            "backend.routers.place.search_places_service",
            return_value=[],
        ) as mock_search,
    ):
        response = client.get(
            SEARCH_URL,
            headers=auth_headers,
            params={"query": "오사카성"},
        )

    assert response.status_code == 200
    mock_search.assert_called_once()


# 7. 인증되지 않은 사용자는 접근 불가
def test_rate_limit_requires_auth(client):
    response = client.get(
        SEARCH_URL,
        params={"query": "오사카성"},
    )

    assert response.status_code == 401
