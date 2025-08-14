from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database Configuration
    database_url: str

    # JWT Configuration
    access_token_secret_key: str
    access_token_expire_minutes: int
    access_token_algorithm: str 

    # MUX Configuration
    mux_secret_key: str
    mux_access_token: str
    
    # Server Configuration
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = True

    # Environment Configuration
    environment: str = 'development'
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()