from functools import cached_property, lru_cache
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.serialization import (
    load_ssh_private_key,
    load_ssh_public_key,
)
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBConfig(BaseSettings):
    db_dialect: str = "postgresql"
    db_driver: str = "asyncpg"
    db_username: str = "postgres"
    db_password: str = "postgres"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "main"

    db_max_connections: int = 25
    db_reserve_connections: float = 0.2

    @property
    def db_url(self) -> str:
        url = (
            f"{self.db_dialect}+{self.db_driver}://"
            f"{self.db_username}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
        return url

    @property
    def db_max_overflow(self) -> int:
        return round(self.db_max_connections * self.db_reserve_connections)

    @property
    def db_pool_size(self) -> int:
        return self.db_max_connections - self.db_max_overflow


class AppConfig(DBConfig):
    model_config = SettingsConfigDict(secrets_dir="/app/secrets")

    version: str = "0.0.1"
    production: bool
    log_dir: Path = Path("/app/log")
    log_config_path: Path = Path("/app/src/log/config.json")

    workers: int = 1
    web_host: str = "0.0.0.0"
    web_port: int = 8080
    web_root_path: str = ""

    images_dir: Path = Path("/app/cache/images")
    dicom_dir: Path = Path("/app/data/dicoms")
    models_dir: Path = Path("/app/models")

    admin_token_header: str = "X-Token"
    admin_token: SecretStr
    jwt_private_key: SecretStr
    jwt_public_key: SecretStr

    @cached_property
    def loaded_jwt_keys(self) -> tuple[Any, Any]:
        private_key = load_ssh_private_key(
            self.jwt_private_key.get_secret_value().encode("utf-8"), password=None
        )
        public_key = load_ssh_public_key(
            self.jwt_public_key.get_secret_value().encode("utf-8")
        )
        return private_key, public_key


@lru_cache
def get_config() -> AppConfig:
    config = AppConfig.model_validate({})
    return config
