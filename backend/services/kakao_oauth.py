import os
from urllib import response
from urllib.parse import urlencode

import httpx
from dotenv import load_dotenv

load_dotenv()

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")

KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USERINFO_URL = "https://kapi.kakao.com/v2/user/me"


def get_kakao_login_url() -> str:
    params = {
        "client_id": KAKAO_REST_API_KEY,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "response_type": "code",
    }

    return f"{KAKAO_AUTH_URL}?{urlencode(params)}"


def get_kakao_access_token(code: str) -> str:
    data = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_REST_API_KEY,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "code": code,
    }

    if KAKAO_CLIENT_SECRET:
        data["client_secret"] = KAKAO_CLIENT_SECRET

    response = httpx.post(
        KAKAO_TOKEN_URL,
        data=data,
        timeout=10.0,
    )
    print("KAKAO STATUS:", response.status_code)
    print("KAKAO ERROR:", response.text)
    response.raise_for_status()

    result = response.json()

    return result["access_token"]


def get_kakao_user_info(access_token: str) -> dict:
    response = httpx.get(
        KAKAO_USERINFO_URL,
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        timeout=10.0,
    )
    print("KAKAO STATUS:", response.status_code)
    print("KAKAO ERROR:", response.text)
    response.raise_for_status()

    return response.json()