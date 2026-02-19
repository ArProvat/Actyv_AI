from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_NAME: str
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    OPENAI_API_KEY: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION_NAME: str
    AWS_S3_BUCKET_NAME: str

    EMBEDDING_CACHE_SIZE: int = 1000
    EMBEDDING_CACHE_TTL: int = 3600*24 
    
    # Search settings
    VECTOR_SEARCH_NUM_CANDIDATES_MULTIPLIER: int = 10
    DEFAULT_MIN_SIMILARITY_SCORE: float = 0.3

    class Config:
        env_file = ".env"

settings = Settings()