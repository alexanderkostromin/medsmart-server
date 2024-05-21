from pathlib import Path

from pydantic_settings import BaseSettings
from sshtunnel import SSHTunnelForwarder


class AlembicConfig(BaseSettings):
    ssh_host: str | None = None
    ssh_port: int | None = None
    ssh_username: str | None = None
    ssh_pkey_file: Path | None = None

    db_dialect: str = "postgresql"
    db_driver: str = "asyncpg"
    db_username: str = "postgres"
    db_password: str = "postgres"
    db_host: str = "localhost"
    db_port: int = 54328
    db_name: str = "main"

    @property
    def db_url(self) -> str:
        url = (
            f"{self.db_dialect}+{self.db_driver}://"
            f"{self.db_username}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
        return url

    def try_create_tunnel(
        self, bind_host: str, bind_port: int
    ) -> SSHTunnelForwarder | None:
        if (
            self.ssh_host is not None
            and self.ssh_port is not None
            and self.ssh_username is not None
            and self.ssh_pkey_file is not None
        ):
            remote_bind_address = (bind_host, bind_port)
            local_bind_address = ("localhost", bind_port)
            return SSHTunnelForwarder(
                (self.ssh_host, self.ssh_port),
                ssh_username=self.ssh_username,
                ssh_pkey=self.ssh_pkey_file,
                remote_bind_address=remote_bind_address,
                local_bind_address=local_bind_address,
            )
        else:
            return None
