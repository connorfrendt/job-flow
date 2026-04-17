from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://job_flow:job_flow@db:5432/job_flow"
    anthropic_api_key: str = ""
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
