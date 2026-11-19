"""
AgroSense AI - Configuration Management
Centralizes all paths, environment variables, and tunable hyperparameters.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
KB_DIR = DATA_DIR / "knowledge_base"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
ASSETS_DIR = BASE_DIR / "assets"
DB_PATH = DATA_DIR / "agrosense.db"
CROPS_CSV = DATA_DIR / "crops.csv"
PESTS_CSV = DATA_DIR / "pests_diseases.csv"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
KB_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE, override=True)
else:
    load_dotenv(override=True)


class AppConfig:
    """Runtime configuration container for AgroSense AI."""

    @staticmethod
    def get_llm_provider() -> str:
        return os.getenv("LLM_PROVIDER", "gemini").lower().strip()

    @staticmethod
    def get_gemini_api_key() -> str:
        return os.getenv("GEMINI_API_KEY", "").strip()

    @staticmethod
    def get_openai_api_key() -> str:
        return os.getenv("OPENAI_API_KEY", "").strip()

    @staticmethod
    def get_anthropic_api_key() -> str:
        return os.getenv("ANTHROPIC_API_KEY", "").strip()

    @staticmethod
    def get_ollama_base_url() -> str:
        return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip()

    @staticmethod
    def get_ollama_model() -> str:
        return os.getenv("OLLAMA_MODEL", "llama3").strip()

    @staticmethod
    def get_retrieval_top_k() -> int:
        try:
            return int(os.getenv("RETRIEVAL_TOP_K", "4"))
        except ValueError:
            return 4

    @staticmethod
    def get_chunk_size() -> int:
        try:
            return int(os.getenv("CHUNK_SIZE", "800"))
        except ValueError:
            return 800

    @staticmethod
    def get_chunk_overlap() -> int:
        try:
            return int(os.getenv("CHUNK_OVERLAP", "150"))
        except ValueError:
            return 150

    @staticmethod
    def get_embedding_provider() -> str:
        return os.getenv("EMBEDDING_PROVIDER", "auto").lower().strip()

    @classmethod
    def update_env_variable(cls, key: str, value: str):
        """Update or insert key=value into .env file and environment."""
        os.environ[key] = value
        lines = []
        if ENV_FILE.exists():
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()

        found = False
        new_lines = []
        for line in lines:
            if line.strip().startswith(f"{key}="):
                new_lines.append(f"{key}={value}\n")
                found = True
            else:
                new_lines.append(line)

        if not found:
            new_lines.append(f"{key}={value}\n")

        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
