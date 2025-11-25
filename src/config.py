from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    
    # API 설정
    API_V1_PREFIX: str = "/fit"
    PROJECT_NAME: str = "AI-TRINITY API"
    VERSION: str = "1.0.0"
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    DEBUG: bool = True
    
    # CORS 설정
    ALLOWED_ORIGINS: str = "https://mefoweb.com,https://api.mefoweb.com,https://care.mefoweb.com,http://localhost:5173"
    
    # 데이터 경로
    REFERENCE_DATA_PATH: str = "outputs/reference_percentiles_real.json"
    
    # OpenAI 설정
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_MAX_TOKENS: int = 800
    OPENAI_TEMPERATURE: float = 0.7

    
    @property
    def allowed_origins_list(self) -> List[str]:
        """CORS 허용 origin 리스트 반환"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 전역 설정 인스턴스
settings = Settings()