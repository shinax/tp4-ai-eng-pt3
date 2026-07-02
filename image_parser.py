"""
Módulo de agentes para el sistema de comparación de imágenes.
Proporciona agentes reutilizables para lectura y comparación de imágenes.
"""

import base64
from pathlib import Path
from typing import Optional
from langfuse.openai import openai
from langfuse import Langfuse

from config import OPENAI_VISION_MODEL

def get_image_media_type(image_path: str) -> str:
    """Determines the media type based on file extension."""
    extension = Path(image_path).suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp"
    }
    return media_types.get(extension, "image/jpeg")

def parse_contract_image(
    image_path: str,
    image_label: str,
    custom_prompt: Optional[str] = None,
    trace_id: Optional[str] = None,
    langfuse_client: Optional[Langfuse] = None,
) -> str:
    """
    Analiza una imagen de contrato y retorna detalles estructurados.

    Args:
        image_path: Ruta a la imagen a analizar
        image_label: Etiqueta para identificar la imagen (ej: "imagen_1", "imagen_2")
        custom_prompt: Prompt personalizado (opcional)
        trace_id: ID del trace de Langfuse (opcional)
        langfuse_client: Cliente de Langfuse (opcional)

    Returns:
        Texto de la imagen.
    """
    langfuse_client = langfuse_client or Langfuse()


    # Codificar imagen a base64
    with open(image_path, "rb") as image_file:
        image_base64 = base64.standard_b64encode(image_file.read()).decode("utf-8")

    image_media_type = get_image_media_type(image_path)  # Llamada para obtener el tipo MIME

    # Usar prompt personalizado o por defecto
    if custom_prompt is None:
        custom_prompt = """
            Analiza esta imagen de un contrato de forma detallada
            y extrae el texto que contiene de la forma más fiel posible

            Reglas generales:
            - No resumas
            - No agregues información
            - Sé conciso, esto va a ser utilizado por otro agente, no por una persona
            - Conserva la estructura general incluyendo numeración

            Proporciona:
            - Objetos principales identificados
            - Texto visible (si lo hay)
            - Si hay texto ilegible márcalo como [ILEGIBLE]
            - Devuelve solo el texto extraido, organizado por secciones."""

    # Llamar a OpenAI con capacidad de visión
    response = openai.chat.completions.create(
        name=f"parse-contract-image-{image_label}",
        trace_id=trace_id,
        model=OPENAI_VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": custom_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{image_media_type};base64,{image_base64}"
                        },
                    },
                ],
            }
        ],
    )

    analysis = response.choices[0].message.content

    return analysis
