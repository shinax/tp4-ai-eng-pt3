"""
Configuración central para la aplicación de comparación de imágenes.
"""

import os
from pathlib import Path
from typing import Optional

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
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

# Configuración de OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Configuración de modelos de IA
IMAGE_ANALYSIS_MODEL = OPENAI_MODEL
IMAGE_COMPARISON_MODEL = OPENAI_MODEL

# Formatos soportados de imágenes
SUPPORTED_IMAGE_FORMATS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp"
}

# Prompts por defecto
DEFAULT_READER_PROMPT = """Analiza estas dos imágenes de forma detallada. 
Para cada imagen, proporciona:
1. Descripción general
2. Objetos principales identificados
3. Colores predominantes
4. Texto visible (si lo hay)
5. Características destacadas

Responde en formato JSON con claves 'imagen_1' e 'imagen_2'."""

DEFAULT_COMPARATOR_PROMPT_TEMPLATE = """Basándote en el siguiente análisis de dos imágenes:

{analysis}

Por favor, realiza una comparación detallada:
1. **Similitudes**: ¿Qué elementos son comunes entre ambas imágenes?
2. **Diferencias principales**: ¿Cuáles son las diferencias más notables?
3. **Diferencias en detalles**: Diferencias en colores, tamaño, posición, etc.
4. **Análisis contextual**: ¿Qué sugieren estas diferencias?
5. **Conclusiones**: Resumen ejecutivo de las diferencias encontradas

Responde en formato JSON con claves: 'similitudes', 'diferencias_principales', 'diferencias_detalles', 'analisis_contextual', 'conclusiones'."""

# Configuración de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENABLE_TRACE_LOGGING = os.getenv("ENABLE_TRACE_LOGGING", "True").lower() == "true"

# Timeouts
OPENAI_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "60"))
IMAGE_READ_TIMEOUT = int(os.getenv("IMAGE_READ_TIMEOUT", "30"))

# Validaciones
def validate_configuration() -> dict:
    """Valida que todas las configuraciones necesarias estén presentes."""
    errors = []
    warnings = []
    
    if not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY no está configurada")
    
    if not LANGFUSE_PUBLIC_KEY:
        warnings.append("LANGFUSE_PUBLIC_KEY no está configurada - las trazas no se enviarán")
    
    if not LANGFUSE_SECRET_KEY:
        warnings.append("LANGFUSE_SECRET_KEY no está configurada - las trazas no se enviarán")
    
    return {
        "errors": errors,
        "warnings": warnings,
        "is_valid": len(errors) == 0
    }


def get_image_media_type(image_path: str) -> str:
    """Obtiene el tipo MIME de una imagen."""
    from pathlib import Path
    
    extension = Path(image_path).suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp"
    }
    return media_types.get(extension, "image/jpeg")


def is_valid_image(image_path: str) -> bool:
    """Verifica si el archivo es una imagen válida."""
    from pathlib import Path
    
    path = Path(image_path)
    
    # Verificar que el archivo existe
    if not path.exists():
        return False
    
    # Verificar que tiene extensión válida
    if path.suffix.lower() not in SUPPORTED_IMAGE_FORMATS:
        return False
    
    # Verificar que es un archivo (no directorio)
    if not path.is_file():
        return False
    
    return True
