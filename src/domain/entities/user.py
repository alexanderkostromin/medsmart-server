import uuid

from pydantic import BaseModel


class UserDomainEntity(BaseModel):
    id: uuid.UUID
    username: str
    is_admin: bool


class UserUpdateDomainEntity(BaseModel):
    username: str
