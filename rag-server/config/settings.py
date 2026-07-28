from pathlib import Path

# Models
EMBED_MODEL = "mxbai-embed-large"

# Chunking
CHUNK_SIZE = 300
CHUNK_OVERLAP = 80

# Ollama
OLLAMA_BASE_URL = "http://host.docker.internal:11434"

# Directories
BASE_DIR = Path(__file__).resolve().parent.parent

VECTOR_STORE_DIR = BASE_DIR / "vector_store"
