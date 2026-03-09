from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Automation Platform"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    SECRET_KEY: str
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_TYPE: str = "mongodb"  # mongodb or mysql
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "automation_platform"
    
    # MySQL
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = ""
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "automation_platform"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # LDAP
    LDAP_ENABLED: bool = True
    LDAP_SERVER: str = ""
    LDAP_BASE_DN: str = ""
    LDAP_USER_DN: str = ""
    LDAP_BIND_USER: str = ""
    LDAP_BIND_PASSWORD: str = ""
    LDAP_SEARCH_FILTER: str = "(uid={username})"
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    GOOGLE_API_KEY: Optional[str] = None
    AI_PROVIDER: str = "openai"  # openai, anthropic, or google
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@automation-platform.com"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "uploads/"
    
    # Task Execution
    MAX_CONCURRENT_TASKS: int = 10
    TASK_TIMEOUT: int = 3600  # 1 hour
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def mysql_url(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
