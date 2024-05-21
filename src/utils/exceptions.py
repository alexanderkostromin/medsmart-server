from http import HTTPStatus
from typing import Any

from fastapi import HTTPException


def exceptions_to_responses(
    *exceptions: HTTPException,
) -> dict[int | str, dict[str, Any]]:
    return {
        e.status_code: {
            "description": e.detail.capitalize(),
            "content": {"application/json": {"example": {"detail": e.detail}}},
        }
        for e in exceptions
    }


def statuses_to_responses(
    *statuses: HTTPStatus,
) -> dict[int | str, dict[str, Any]]:
    return {
        status: {
            "description": f"Error with code {status} and a string description",
            "content": {"application/json": {"example": {"detail": "some detail"}}},
        }
        for status in statuses
    }
