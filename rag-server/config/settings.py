from pathlib import Path

# Models
EMBED_MODEL = "mxbai-embed-large"
OCR_MODEL = "glm-ocr"

# TRANSLATION_MODEL = "qwen3.5:9b"
TRANSLATION_MODEL = "qwen2.5:7b"
# TRANSLATION_MODEL = "translategemma:12b"

RAG_MODEL = "qwen2.5:7b"

# Chunking
CHUNK_SIZE = 300
CHUNK_OVERLAP = 80

# Ollama
OLLAMA_BASE_URL = "http://host.docker.internal:11434"

# Directories
BASE_DIR = Path(__file__).resolve().parent.parent

VECTOR_STORE_DIR = BASE_DIR / "vector_store"


# Database
DB_HOST = "postgres"
DB_PORT = 5432
DB_NAME = "rag"
DB_USER = "postgres"
DB_PASSWORD = "postgres"