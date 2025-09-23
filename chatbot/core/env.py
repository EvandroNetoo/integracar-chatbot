from pathlib import Path

from pydantic_settings import BaseSettings


class EnvSettings(BaseSettings):
    class Config:
        env_file = str(Path(__file__).parent.parent.parent / '.env')
        env_file_encoding = 'utf-8'
        case_sensitive = True

    SECRET_KEY: str = 'change-me'  # noqa: S105
    DEBUG: bool = True
    OPENAI_API_KEY: str = ''
    GROQ_API_KEY: str = ''
    VOYAGE_API_KEY: str = ''


env = EnvSettings()
