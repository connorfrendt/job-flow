from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://jobflow:jobflow@db:5432/jobflow"
    anthropic_api_key: str = ""
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
