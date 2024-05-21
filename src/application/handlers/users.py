import uuid
from http import HTTPStatus

import sqlalchemy as sa
from fastapi import APIRouter, HTTPException, Response

from application.dependencies.auth import AuthDep
from application.dependencies.session import AsyncSessionDep
from application.exceptions import UNAUTHORIZED_ERROR
from config import get_config
from domain.entities import UserDomainEntity
from domain.entities.jwt import AuthRole
from infrastructure.entities import User
from utils.exceptions import exceptions_to_responses

router = APIRouter(
    tags=["Users"],
    prefix="/users",
    responses=exceptions_to_responses(UNAUTHORIZED_ERROR),
)


@router.get("/all", response_model=list[UserDomainEntity])
async def get_all_users(auth: AuthDep, session: AsyncSessionDep):
    stmt = sa.select(User)
    res = await session.execute(stmt)
    return res.scalars().all()


@router.get("/{username}", response_model=UserDomainEntity)
async def get_user(username: str, auth: AuthDep, session: AsyncSessionDep):
    stmt = sa.select(User).where(User.username == username)
    res = await session.execute(stmt)
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(HTTPStatus.NOT_FOUND, "user not found")
    return user


@router.patch("/{username}/promote")
async def promote_user(username: str, auth: AuthDep, session: AsyncSessionDep):
    if AuthRole.ADMIN not in auth.roles:
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, "you are not authorized for this operation"
        )

    stmt = sa.select(User).where(User.username == username)
    res = await session.execute(stmt)
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(HTTPStatus.NOT_FOUND, "user not found")

    user.is_admin = True
    await session.commit()
    return Response(status_code=HTTPStatus.NO_CONTENT)


@router.patch("/{username}/demote")
async def demote_user(username: str, auth: AuthDep, session: AsyncSessionDep):
    if AuthRole.ADMIN not in auth.roles:
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, "you are not authorized for this operation"
        )

    stmt = sa.select(User).where(User.username == username)
    res = await session.execute(stmt)
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(HTTPStatus.NOT_FOUND, "user not found")

    user.is_admin = False
    await session.commit()
    return Response(status_code=HTTPStatus.NO_CONTENT)
