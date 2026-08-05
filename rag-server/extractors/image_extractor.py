
from pathlib import Path

from ollama import Client, chat

from config.settings import (
    OLLAMA_BASE_URL,
    OCR_MODEL,
)
client = Client(host=OLLAMA_BASE_URL)

def image_extract(file_path: Path) -> str:
    try:
        response = client.chat(
            model=OCR_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Extract all visible text from this image "
                        "exactly as it appears."
                    ),
                    "images": [str(file_path)],
                }
            ],
            options={
                "num_ctx": 20480,
                "num_predict": 2048,
                "temperature": 0,
            },
        )

        return response.message.content

    except Exception as e:
        raise RuntimeError(
            f"OCR failed: {e}"
        ) from e