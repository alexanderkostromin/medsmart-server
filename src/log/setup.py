import atexit
import json
import logging.config
from pathlib import Path


def setup_logging(log_config_path: Path) -> None:
    with open(log_config_path) as f:
        log_config = json.load(f)
    logging.config.dictConfig(log_config)
    queue_handler = logging.getHandlerByName("queue")
    if queue_handler is not None:
        queue_handler.listener.start()  # type: ignore
        atexit.register(queue_handler.listener.stop)  # type: ignore
