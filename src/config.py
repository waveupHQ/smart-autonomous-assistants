import os
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()  # This loads the variables from .env


class Settings(BaseSettings):
    # Project settings
    PROJECT_NAME: str = "SAA-Orchestrator"

    # VertexAI settings
    PROJECT_ID: str = os.getenv("VertexAI_Project_Name")
    LOCATION: str = os.getenv("VertexAI_Location")

    @property
    def anthropic_api_key(self) -> str:
        if not self.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not set in the environment")
        return self.ANTHROPIC_API_KEY

    @property
    def openai_api_key(self) -> str:
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in the environment")
        return self.OPENAI_API_KEY

    @property
    def tavily_api_key(self) -> str:
        if not self.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY is not set in the environment")
        return self.TAVILY_API_KEY

    # API Keys
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    # Assistant settings
    MAIN_ASSISTANT: str = "claude-3-sonnet-20240229"
    SUB_ASSISTANT: str = "claude-3-haiku-20240307"
    REFINER_ASSISTANT: str = "gemini-1.5-pro-preview-0409"

    # Fallback models
    FALLBACK_MODEL_1: str = "gpt-3.5-turbo"
    FALLBACK_MODEL_2: str = "gpt-3.5-turbo"

    # Tools
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")

    # New setting for SAAsWorkers
    NUM_WORKERS: int = 3

    class Config:
        env_file = ".env"
        extra = "ignore"  # This will ignore any extra fields in the environment


settings = Settings()
