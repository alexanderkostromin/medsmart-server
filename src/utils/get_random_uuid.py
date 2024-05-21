from sqlalchemy import UUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression as expr


class GetRandomUUID(expr.FunctionElement):
    type = UUID()


@compiles(GetRandomUUID, "postgresql")
def compile_get_random_uuid(element, compiler, **kw) -> str:
    return "gen_random_uuid()"
