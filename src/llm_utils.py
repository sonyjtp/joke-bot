import os

from langchain_core.language_models import BaseChatModel

from src.chat_model import BaseModelConfig
from src.config import LLM_MAP, LLM_PROVIDERS


def get_llm(model_config: BaseModelConfig) -> BaseChatModel:
    for provider in LLM_PROVIDERS:
        if provider["default_model"] == model_config.model_name: #TODO fix this later
            api_key = os.getenv(provider["api_key_env"])
            if api_key:
                kwargs = {
                    provider["api_key_param"]: api_key,
                    "model": model_config.model_name,
                    "temperature": model_config.temperature,
                }
                return provider["class"](**kwargs)
    raise RuntimeError("No valid LLM provider found for model: {}".format(model_config.model_name))
