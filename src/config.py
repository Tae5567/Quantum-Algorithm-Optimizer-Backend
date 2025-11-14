from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_access_key_id: str
    aws_secret_access_key: str
    
    # Bedrock Configuration
    bedrock_model_id: str = "amazon.nova-pro-v1:0"
    bedrock_region: str = "us-east-1"
    
    # Braket Configuration
    braket_s3_bucket: str
    braket_region: str = "us-east-1"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # CORS - now handles comma-separated string OR JSON array
    allowed_origins: str = "http://localhost:3000,http://localhost:3001"
    
    @property
    def origins_list(self) -> List[str]:
        """Convert comma-separated string to list"""
        if isinstance(self.allowed_origins, str):
            return [origin.strip() for origin in self.allowed_origins.split(',')]
        return self.allowed_origins
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()