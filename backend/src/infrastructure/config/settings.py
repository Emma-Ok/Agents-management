from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    """
    Configuración centralizada usando Pydantic
    
    Lee automáticamente las variables de entorno y las valida
    """
    # App settings
    app_name: str = "AI Agents Manager"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    api_prefix: str = "/api/v1"
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000"]
    
    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "ai_agents_db"
    mongodb_max_pool_size: int = 10
    mongodb_min_pool_size: int = 1
    
    # AWS S3
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_s3_bucket_name: str = "ai-agents-documents"
    aws_s3_region: str = "us-east-1"
    aws_s3_endpoint_url: str = "https://s3.amazonaws.com"
    
    # File upload
    allowed_extensions: List[str] = ["pdf", "docx", "xlsx", "pptx", "txt", "csv"]
    max_file_size_mb: int = 10
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def cors_origins(self) -> List[str]:
        if isinstance(self.allowed_origins, str):
            return [origin.strip() for origin in self.allowed_origins.split(",")]
        return self.allowed_origins

@lru_cache()
def get_settings() -> Settings:
    """Singleton para obtener la configuración"""
    return Settings()