from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = 'postgresql+asyncpg://app:devpassword@localhost:5432/plancraft3d'
    redis_url: str = 'redis://localhost:6379'
    jwt_secret: str = 'change-me-to-a-random-64-char-string'
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    storage_backend: str = 'local'
    storage_path: str = './data/uploads'
    s3_bucket: str = 'plancraft3d-uploads'
    s3_region: str = 'us-east-1'

    model_config = {
        'env_file': ('.env', '../.env', '../../.env'),
        'env_file_encoding': 'utf-8',
        'extra': 'ignore',
    }


settings = Settings()
