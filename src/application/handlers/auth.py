from http import HTTPStatus

import jwt
import sqlalchemy as sa
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

from application.dependencies.auth import AuthDep
from application.dependencies.config import ConfigDep
from application.dependencies.session import AsyncSessionDep
from domain.entities.jwt import AuthRole, AuthUser, JWTPayload
from infrastructure.entities import User
from utils.cookies import clear_jwt_cookies, set_jwt_cookies
from utils.exceptions import statuses_to_responses
from utils.password import check_password, get_hashed_password

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses=statuses_to_responses(HTTPStatus.CONFLICT, HTTPStatus.FORBIDDEN),
)


class AuthProps(BaseModel):
    username: str
    password: str


@router.post("/register")
async def register(props: AuthProps, *, session: AsyncSessionDep, config: ConfigDep):
    if config.production:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="registration suspended"
        )  # HACK disables registration in production

    stmt = sa.select(User).where(User.username == props.username)
    res = await session.execute(stmt)
    user = res.scalar_one_or_none()

    if user:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="username taken")

    password_hash = get_hashed_password(props.password.encode("utf-8")).decode("utf-8")
    user = User()
    user.username = props.username
    user.password_hash = password_hash
    session.add(user)
    await session.commit()
    await session.refresh(user)

    response = Response()
    auth_user = AuthUser.model_validate(user)
    payload = JWTPayload(roles=[], user=auth_user)
    jwt_private_key, _ = config.loaded_jwt_keys
    jwt_token = jwt.encode(
        payload=payload.model_dump(), key=jwt_private_key, algorithm="RS256"
    )
    set_jwt_cookies(response, jwt_token)

    return response


@router.post("/login")
async def login(props: AuthProps, *, session: AsyncSessionDep, config: ConfigDep):
    stmt = sa.select(User).where(User.username == props.username)
    res = await session.execute(stmt)
    user = res.scalar_one_or_none()

    if not user:
        raise HTTPException(HTTPStatus.FORBIDDEN, "invalid credentials")

    if not check_password(
        props.password.encode("utf-8"), user.password_hash.encode("utf-8")
    ):
        raise HTTPException(HTTPStatus.FORBIDDEN, "invalid credentials")

    auth_user = AuthUser.model_validate(user)
    auth_roles: list[AuthRole] = []
    if user.is_admin:
        auth_roles.append(AuthRole.ADMIN)
    payload = JWTPayload(roles=auth_roles, user=auth_user)

    response = Response()
    jwt_private_key, _ = config.loaded_jwt_keys
    jwt_token = jwt.encode(
        payload=payload.model_dump(), key=jwt_private_key, algorithm="RS256"
    )
    set_jwt_cookies(response, jwt_token)

    return response


@router.get("/logout")
async def logout():
    response = Response()
    clear_jwt_cookies(response)
    return response


@router.get("/check")
async def check(*, auth: AuthDep):
    return Response(status_code=200)
