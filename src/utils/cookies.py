from datetime import datetime, timedelta, timezone
from enum import StrEnum

from fastapi import Response


class CookieKey(StrEnum):
    JWT_HEADER_PAYLOAD = "auth"
    JWT_SIGNATURE = "sign"


def set_jwt_cookies(response: Response, jwt_token: str) -> None:
    header, payload, signature = jwt_token.split(".")
    js_cookie = f"{header}.{payload}"
    http_cookie = signature
    in_30_min = datetime.now(timezone.utc) + timedelta(minutes=30)

    response.set_cookie(
        key=CookieKey.JWT_HEADER_PAYLOAD,
        value=js_cookie,
        secure=True,
        expires=in_30_min,
    )
    response.set_cookie(
        key=CookieKey.JWT_SIGNATURE,
        value=http_cookie,
        secure=True,
        httponly=True,
    )


def clear_jwt_cookies(response: Response) -> None:
    response.delete_cookie(CookieKey.JWT_HEADER_PAYLOAD)
    response.delete_cookie(CookieKey.JWT_SIGNATURE)
