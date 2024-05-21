import logging
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import override

LOGGING_FMT = (
    "%(asctime)s | %(levelname)s: %(message)s @ %(name)s/%(funcName)s:%(lineno)d"
)


# def format_logging_time(
#     record: logging.LogRecord,
#     datefmt: str | None = None,
# ) -> str:
#     return (
#         datetime.fromtimestamp(record.created, timezone.utc)
#         .astimezone()
#         .isoformat(sep="T", timespec="seconds")
#     )


class MyFormatter(logging.Formatter):
    @override
    def formatTime(self, record, datefmt=None) -> str:
        return (
            datetime.fromtimestamp(record.created, timezone.utc)
            .astimezone()
            .isoformat(sep="T", timespec="seconds")
        )


def setup_stream_handler(
    logger: logging.Logger = logging.root,
    *,
    level: int | str,
    stream=sys.stderr,
    format: str = LOGGING_FMT,
) -> None:
    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    formatter = MyFormatter(format)
    # formatter.formatTime = format_logging_time  # type: ignore[method-assign]
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def setup_file_handler(
    logfile: Path,
    logger: logging.Logger = logging.root,
    *,
    level: int | str,
    format: str = LOGGING_FMT,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 10,
) -> None:
    handler = RotatingFileHandler(
        logfile,
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    handler.setLevel(level)
    formatter = MyFormatter(format)
    # formatter.formatTime = format_logging_time  # type: ignore[method-assign]
    handler.setFormatter(formatter)
    logger.addHandler(handler)
