
from unittest.mock import patch
from uuid import uuid4

import pytest

from backend.cache import get_redis_client
from backend.services.place import (
    make_place_cache_key,
    search_places_service,
)


def test_real_redis_cache_hit_and_miss():
    redis_client = get_redis_client()

    try:
        redis_client.ping()
    except Exception:
        pytest.skip("Real Redis server is not available")

    # 다른 테스트의 캐시와 겹치지 않는 검색어
    query = f"day20-test-{uuid4().hex}"

    cache_key = make_place_cache_key(
        query=query,
        latitude=None,
        longitude=None,
    )

    mock_google_response = {
        "places": [
            {
                "id": "day20-place-1",
                "displayName": {
                    "text": "Day20 테스트 장소",
                },
                "formattedAddress": "Seoul, Korea",
                "location": {
                    "latitude": 37.5665,
                    "longitude": 126.9780,
                },
                "primaryType": "tourist_attraction",
            }
        ]
    }

    try:
        # 1. 첫 번째 검색: Cache Miss
        with patch(
            "backend.services.place.request_google_places",
            return_value=mock_google_response,
        ) as mock_google:
            first_result = search_places_service(query)
            mock_google.assert_called_once()

        assert len(first_result) == 1
        assert first_result[0].name == "Day20 테스트 장소"

        # Redis에 실제로 저장됐는지 확인
        assert redis_client.exists(cache_key) == 1

        # TTL 확인
        ttl = redis_client.ttl(cache_key)

        assert 0 < ttl <= 1800

        # 2. 두 번째 검색: Cache Hit
        with patch(
            "backend.services.place.request_google_places",
        ) as mock_google:
            second_result = search_places_service(query)

            # Cache Hit이므로 Google 호출 0회
            mock_google.assert_not_called()

        assert len(second_result) == 1
        assert second_result[0].name == "Day20 테스트 장소"

        assert second_result == first_result

    finally:
        # 테스트가 만든 키만 삭제
        redis_client.delete(cache_key)
