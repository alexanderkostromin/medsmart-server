import uuid
from enum import StrEnum, auto

from pydantic import BaseModel, ConfigDict, field_serializer


class AuthRole(StrEnum):
    ADMIN = auto()


class AuthUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str | None = None

    @field_serializer("id")
    def serialize_id(self, id: uuid.UUID, _info) -> str:
        return str(id)


class JWTPayload(BaseModel):
    roles: list[AuthRole]
    user: AuthUser | None = None
