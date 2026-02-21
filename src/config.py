from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

# files and directories
DATA_DIR = "data"
CONFIG_DIR = "config"
OUTPUTS_DIR = "outputs"
CONFIG_FILE_NAME = "config.yaml"
PROMPT_CONFIG_FILE_NAME = "prompt_config.yaml"

# model configurations
CRITIC_MODEL="llama-3.1-8b-instant" #"gpt-4o-mini"
CRITIC_TEMPERATURE=0.1
WRITER_MODEL="llama-3.1-8b-instant" #"gpt-4o-mini"
WRITER_TEMPERATURE=0.8

LLM_PROVIDERS = [
    {
        "api_key_env": "GROQ_API_KEY",
        "model_env": "GROQ_MODEL",
        "default_model": "llama-3.1-8b-instant",
        "name": "Groq",
        "class": ChatGroq,
        "api_key_param": "api_key",
    },
    {
        "api_key_env": "GOOGLE_API_KEY",
        "model_env": "GOOGLE_MODEL",
        "default_model": "gemini-2.0-flash",
        "name": "Google Gemini",
        "class": ChatGoogleGenerativeAI,
        "api_key_param": "google_api_key",
    },
    {
        "api_key_env": "OPENAI_API_KEY",
        "model_env": "OPENAI_MODEL",
        "default_model": "gpt-4o-mini",
        "name": "OpenAI",
        "class": ChatOpenAI,
        "api_key_param": "api_key",
    },
]

LLM_MAP = {
    "gpt-4o-mini": ChatOpenAI,
    "llama3-8b-8192": ChatGroq,
}


JOKE_LANGUAGES = ["en", "de", "es", "fr", "it", "ru", "sv"]


# prompt_cfg = load_config(PROMPT_CONFIG_FILE_PATH)