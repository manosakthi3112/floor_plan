from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = 'redis://localhost:6379'
    model_path: str = '/models/floorplan_yolov8.pt'
    model_confidence: float = 0.5

    model_config = {'env_file': '.env', 'env_file_encoding': 'utf-8'}


settings = Settings()
