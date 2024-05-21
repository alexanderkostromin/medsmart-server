from datetime import datetime

from sqlalchemy import DDL, Connection, DDLElement, FetchedValue, MetaData
from sqlalchemy.ext import compiler
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import functions as func

CREATE_UPDATED_AT_TRIGGER_FUNC = DDL(
    """\
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;   
END;
$$ language 'plpgsql';"""
)


class AuditMixin:
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        sort_order=900,
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        server_onupdate=FetchedValue(for_update=True),
        sort_order=901,
    )


class CreateUpdatedAtTrigger(DDLElement):
    def __init__(self, name: str):
        self.name = name


class DropUpdatedAtTrigger(DDLElement):
    def __init__(self, name: str):
        self.name = name


def get_updated_at_trigger_name(qualified_name: str) -> str:
    return f"trigger__updated_at_{qualified_name}"


@compiler.compiles(CreateUpdatedAtTrigger)
def compile_create_trigger(element: CreateUpdatedAtTrigger, compiler, **kw) -> str:
    trigger_name = get_updated_at_trigger_name(element.name)
    return f"""\
CREATE OR REPLACE TRIGGER {trigger_name}
BEFORE UPDATE ON "{element.name}"
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at_column()
"""


@compiler.compiles(DropUpdatedAtTrigger)
def compile_drop_trigger(element: DropUpdatedAtTrigger, compiler, **kw) -> str:
    trigger_name = get_updated_at_trigger_name(element.name)
    return f"DROP TRIGGER {trigger_name}"


def create_updated_at_triggers(connection: Connection, target: MetaData, **kw):
    connection.execute(CREATE_UPDATED_AT_TRIGGER_FUNC)
    for table in target.tables.values():
        if not table.name.startswith("view_"):
            connection.execute(CreateUpdatedAtTrigger(table.name))
    connection.commit()


def drop_updated_at_triggers(connection: Connection, target: MetaData, **kw):
    for table in target.tables.values():
        connection.execute(DropUpdatedAtTrigger(table.name))
    connection.commit()
