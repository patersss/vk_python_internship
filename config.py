from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_db: str
    postgres_password: str
    secret_key: str

    lock_timeout_seconds: int = 300

    @property
    def db_url(self):
        return (f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:"
                f"{self.postgres_port}/{self.postgres_db}")


settings = AppConfig()
