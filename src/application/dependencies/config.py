import functools
from typing import Annotated

from fastapi import Depends

from config import AppConfig


@functools.lru_cache
def get_config() -> AppConfig:
    return AppConfig.model_validate({})


ConfigDep = Annotated[AppConfig, Depends(get_config)]
