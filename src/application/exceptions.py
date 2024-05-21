from http import HTTPStatus

from fastapi import HTTPException

UNAUTHORIZED_ERROR = HTTPException(
    status_code=HTTPStatus.UNAUTHORIZED,
    detail="you are not authorized for this operation",
)

NOT_FOUND_ERROR = HTTPException(
    status_code=HTTPStatus.NOT_FOUND,
    detail="not found",
)
