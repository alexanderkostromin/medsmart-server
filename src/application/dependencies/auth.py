import logging
from http import HTTPStatus
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, Response

from application.dependencies.config import ConfigDep
from config import AppConfig
from domain.entities.jwt import AuthRole, JWTPayload
from utils.cookies import CookieKey, set_jwt_cookies

logger = logging.getLogger(__name__)


def extract_jwt_header(request: Request, config: AppConfig) -> str:
    auth_header = request.headers.get("Authentication")

    if auth_header and len(auth_header.split(" ")) == 2:
        return auth_header

    header_and_payload = request.cookies.get(CookieKey.JWT_HEADER_PAYLOAD)
    signature = request.cookies.get(CookieKey.JWT_SIGNATURE)
    if header_and_payload and signature:
        jwt_token = f"{header_and_payload}.{signature}"
        return f"JWT {jwt_token}"

    admin_token = config.admin_token.get_secret_value()
    admin_token_header = config.admin_token_header
    token = request.headers.get(admin_token_header)
    if token and token == admin_token:
        jwt_private_key, _ = config.loaded_jwt_keys
        payload = JWTPayload(roles=[AuthRole.ADMIN]).model_dump()
        jwt_token = jwt.encode(payload, key=jwt_private_key, algorithm="RS256")
        return f"JWT {jwt_token}"

    raise HTTPException(HTTPStatus.FORBIDDEN, "not authenticated")


def auth(request: Request, response: Response, config: ConfigDep) -> JWTPayload:
    jwt_header = extract_jwt_header(request, config)
    _, jwt_token = jwt_header.split(" ")

    jwt_private_key, jwt_public_key = config.loaded_jwt_keys

    try:
        data = jwt.decode(jwt_token, key=jwt_public_key, algorithms=["RS256"])
        payload = JWTPayload.model_validate(data)
    except Exception as e:
        logger.error(e)
        raise HTTPException(HTTPStatus.FORBIDDEN, "not authenticated")

    jwt_token = jwt.encode(
        payload=payload.model_dump(), key=jwt_private_key, algorithm="RS256"
    )
    set_jwt_cookies(response, jwt_token)  # refresh cookies expiration date

    return payload


AuthDep = Annotated[JWTPayload, Depends(auth)]
