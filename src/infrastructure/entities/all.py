import uuid

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.entities.mixins.audit import AuditMixin
from utils.get_random_uuid import GetRandomUUID


class Base(AuditMixin, sa_orm.DeclarativeBase):
    metadata = sa.MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

    @sa_orm.declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(
        sa.Integer,
        sa.Identity(),
        primary_key=True,
        index=True,
        sort_order=-10,
    )

    def __str__(self) -> str:
        properties = [
            f"{name}={value!r}"
            for column in self.__table__.columns
            if (name := column.name) not in ("created_at", "updated_at")
            and (value := getattr(self, name)) is not None
        ]
        return f"{self.__class__.__name__}({', '.join(properties)})"

    def __repr__(self) -> str:
        properties = [
            f"{column.name}={getattr(self, column.name)!r}"
            for column in self.__table__.columns
        ]
        return f"<{self.__class__.__name__}({', '.join(properties)})>"


class User(Base):
    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID,
        primary_key=True,
        index=True,
        server_default=GetRandomUUID(),
        sort_order=-10,
    )

    username: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str] = mapped_column()
    is_admin: Mapped[bool] = mapped_column(server_default=sa.false())
