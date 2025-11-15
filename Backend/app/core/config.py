"""
Core configuration module for the ArqLeads System.
Handles all environment variables and application settings.
"""

from typing import List, Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "ArqLeads System"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    VERSION: str = "1.0.0"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://user:pass@localhost:5432/arqleads",
        description="Database connection string"
    )
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50
    
    # AI Provider
    AI_PROVIDER: str = "openai"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 500
    OPENAI_TEMPERATURE: float = 0.7
    
    # Anthropic
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    ANTHROPIC_MAX_TOKENS: int = 500

    # Ollama (local, free)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"
    OLLAMA_MAX_TOKENS: int = 2048
    OLLAMA_TEMPERATURE: float = 0.7

    # Security
    SECRET_KEY: str = Field(
        default="change-this-in-production",
        min_length=32
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if not v or v.strip() == "":
                return ["http://localhost:3000", "http://localhost:5173"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_ENABLED: bool = True
    
    # Email
    SMTP_ENABLED: bool = True
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@arqleads.com"
    SMTP_FROM_NAME: str = "ArqLeads System"
    NOTIFICATION_EMAILS: List[str] = ["admin@example.com"]
    
    @validator("NOTIFICATION_EMAILS", pre=True)
    def parse_notification_emails(cls, v):
        if isinstance(v, str):
            if not v or v.strip() == "":
                return ["admin@example.com"]
            return [email.strip() for email in v.split(",") if email.strip()]
        return v
    
    EMAIL_TEMPLATES_DIR: str = "./app/templates/emails"
    
    # WhatsApp
    WHATSAPP_ENABLED: bool = False
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_WHATSAPP_NUMBER: Optional[str] = None
    TWILIO_RECIPIENT_NUMBER: Optional[str] = None
    
    # SMS
    SMS_ENABLED: bool = False
    SMS_PROVIDER: str = "twilio"
    SMS_HOT_LEADS_ENABLED: bool = True
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_ALWAYS_EAGER: bool = False
    
    # Lead Scoring
    SCORING_PROJECT_DEFINED: int = 20
    SCORING_BUDGET_HIGH: int = 25
    SCORING_TIMELINE_SHORT: int = 30
    SCORING_CONTACT_COMPLETE: int = 15
    SCORING_LOCATION_DEFINED: int = 10
    
    SCORE_THRESHOLD_COLD: int = 30
    SCORE_THRESHOLD_WARM: int = 60
    SCORE_THRESHOLD_HOT: int = 61
    
    # Business Configuration
    STUDIO_NAME: str = "Estudio de Arquitectura"
    STUDIO_LOCATION: str = "Vigo, Galicia"
    STUDIO_SPECIALTIES: str = "viviendas unifamiliares,reformas integrales"
    
    MIN_BUDGET_THRESHOLD: int = 15000
    MAX_HOT_TIMELINE_MONTHS: int = 3
    
    # Chatbot
    CHATBOT_NAME: str = "AsistenteArq"
    CHATBOT_PERSONALITY: str = "profesional y amigable"
    CHATBOT_LANGUAGE: str = "es"
    CHATBOT_MAX_CONVERSATION_LENGTH: int = 20
    CHATBOT_TIMEOUT_MINUTES: int = 15
    
    # Monitoring
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "./logs/app.log"
    
    SENTRY_ENABLED: bool = False
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "development"
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: str = "pdf,jpg,jpeg,png,dwg"
    UPLOAD_DIR: str = "./uploads"
    
    # Analytics
    ANALYTICS_ENABLED: bool = True
    ANALYTICS_RETENTION_DAYS: int = 90
    EXPORT_FORMAT: str = "csv"
    
    # Feature Flags
    FEATURE_WHATSAPP: bool = False
    FEATURE_VOICE_NOTES: bool = False
    FEATURE_APPOINTMENT_BOOKING: bool = True
    FEATURE_CRM_INTEGRATION: bool = False
    FEATURE_MULTILANGUAGE: bool = False
    
    # Integrations
    GOOGLE_CALENDAR_ENABLED: bool = False
    GOOGLE_CALENDAR_CREDENTIALS_FILE: str = "./credentials/google_calendar.json"
    
    CRM_ENABLED: bool = False
    CRM_TYPE: str = "hubspot"
    CRM_API_KEY: Optional[str] = None
    
    # Performance
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 3600
    SESSION_EXPIRE_MINUTES: int = 30
    
    # Testing
    TESTING: bool = False
    MOCK_AI_RESPONSES: bool = False
    DISABLE_AUTH_FOR_TESTING: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @property
    def database_url_sync(self) -> str:
        """Convert async database URL to sync version."""
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    
    @property
    def studio_specialties_list(self) -> List[str]:
        """Parse studio specialties as list."""
        return [s.strip() for s in self.STUDIO_SPECIALTIES.split(",")]
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """Parse allowed file types as list."""
        return [t.strip() for t in self.ALLOWED_FILE_TYPES.split(",")]
    
    def get_ai_config(self) -> dict:
        """Get AI provider configuration."""
        if self.AI_PROVIDER == "openai":
            return {
                "provider": "openai",
                "api_key": self.OPENAI_API_KEY,
                "model": self.OPENAI_MODEL,
                "max_tokens": self.OPENAI_MAX_TOKENS,
                "temperature": self.OPENAI_TEMPERATURE,
            }
        elif self.AI_PROVIDER == "anthropic":
            return {
                "provider": "anthropic",
                "api_key": self.ANTHROPIC_API_KEY,
                "model": self.ANTHROPIC_MODEL,
                "max_tokens": self.ANTHROPIC_MAX_TOKENS,
            }
        elif self.AI_PROVIDER == "ollama":
            return {
                "provider": "ollama",
                "base_url": self.OLLAMA_BASE_URL,
                "model": self.OLLAMA_MODEL,
                "max_tokens": self.OLLAMA_MAX_TOKENS,
                "temperature": self.OLLAMA_TEMPERATURE,
            }
        else:
            raise ValueError(f"Unknown AI provider: {self.AI_PROVIDER}")
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()