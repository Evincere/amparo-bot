"""
Configuración centralizada de la aplicación.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configuración de la aplicación con validación."""
    
    # Ollama Cloud (Fallback/Backup)
    ollama_api_key: str = "local"
    ollama_model: str = "gpt-oss:120b"
    ollama_host: str = "https://ollama.com"
    
    # Groq Chat
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    
    # Embeddings
    embedding_provider: str = "huggingface" # "ollama" or "huggingface"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # CORS
    cors_origins: str = "https://defensamendoza.gob.ar"
    
    # Knowledge Base
    knowledge_file: str = "data/knowledge.json"
    
    # SSL
    ssl_verify: bool = False
    
    
    # Session
    session_timeout: int = 3600
    
    # Admin
    admin_api_key: str = ""
    
    # Logging
    log_level: str = "INFO"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convierte CORS_ORIGINS string a lista."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()
