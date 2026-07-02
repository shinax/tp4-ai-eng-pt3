"""
Configuración central para la aplicación de comparación de imágenes.
"""

import os
from pathlib import Path

# Directorios
PROJECT_ROOT = Path(__file__).parent
EXAMPLES_DIR = PROJECT_ROOT / "examples"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Crear directorios si no existen
EXAMPLES_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Configuración de Langfuse
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
LANGFUSE_BASE_URL = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
LANGFUSE_PROJECT_ID = os.getenv("LANGFUSE_PROJECT_ID", "")
LANGFUSE_PROJECT_URL = (
    f"{LANGFUSE_BASE_URL}/projects/{LANGFUSE_PROJECT_ID}" if LANGFUSE_PROJECT_ID else ""
)

# Configuración de OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Configuración de modelos de IA
OPENAI_VISION_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4o")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# Configuración de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")