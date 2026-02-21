from pydantic import BaseModel

from src.config import WRITER_MODEL, WRITER_TEMPERATURE, CRITIC_MODEL, CRITIC_TEMPERATURE


class BaseModelConfig(BaseModel):
    model_name: str
    temperature: float

class WriterModel(BaseModelConfig):
    model_name: str = WRITER_MODEL
    temperature: float = WRITER_TEMPERATURE

class CriticModel(BaseModelConfig):
    model_name: str = CRITIC_MODEL
    temperature: float = CRITIC_TEMPERATURE