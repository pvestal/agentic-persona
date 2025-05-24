"""Configuration settings for ECHO Backend"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application
    app_name: str = "ECHO - Evolving Cognitive Helper & Orchestrator"
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    
    # API Keys
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    
    # Database
    database_url: str = Field(default="sqlite+aiosqlite:///./database/echo.db")
    
    # Firebase (Production)
    firebase_credentials: Optional[str] = Field(default=None)
    firebase_project_id: Optional[str] = Field(default=None)
    
    # Redis (Optional)
    redis_url: Optional[str] = Field(default=None)
    
    # CORS - handled separately to avoid pydantic parsing issues
    cors_origins: List[str] = Field(default=["http://localhost:5173", "http://localhost:3000"])
    
    # Agent Settings
    max_agent_iterations: int = 10
    agent_timeout: int = 300  # seconds
    
    # ECHO Specific Settings
    style_morph_enabled: bool = True
    evolution_enabled: bool = True
    auto_learning: bool = True
    default_autonomy_level: str = "suggest"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()