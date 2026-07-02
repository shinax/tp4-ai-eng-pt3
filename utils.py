"""
Utilidades para la aplicación de comparación de imágenes.
"""

import json
import logging
from typing import Any, Dict
from datetime import datetime
from pathlib import Path

from config import LOG_LEVEL, OUTPUT_DIR


# Configurar logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def save_json(data: str, trace_id: str) -> Path:
    """Guarda resultados en formato JSON."""
    filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{trace_id}.json"
    filepath = OUTPUT_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Resultados guardados en: {filepath}")
    return filepath


class ConsoleFormatter:
    """Formatea la salida para consola."""

    # Colores ANSI
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "cyan": "\033[96m",
    }

    @staticmethod
    def print_header(text: str):
        """Imprime un encabezado."""
        color = ConsoleFormatter.COLORS
        print(f"\n{color['bold']}{color['cyan']}{'=' * 70}{color['reset']}")
        print(f"{color['bold']}{color['cyan']}{text}{color['reset']}")
        print(f"{color['bold']}{color['cyan']}{'=' * 70}{color['reset']}\n")

    @staticmethod
    def print_section(title: str):
        """Imprime un título de sección."""
        color = ConsoleFormatter.COLORS
        print(f"{color['bold']}{color['blue']}{title}{color['reset']}")
        print(f"{color['blue']}{'-' * len(title)}{color['reset']}")

    @staticmethod
    def print_success(message: str):
        """Imprime un mensaje de éxito."""
        color = ConsoleFormatter.COLORS
        print(f"{color['green']}✅ {message}{color['reset']}")

    @staticmethod
    def print_error(message: str):
        """Imprime un mensaje de error."""
        color = ConsoleFormatter.COLORS
        print(f"{color['red']}❌ {message}{color['reset']}")

    @staticmethod
    def print_warning(message: str):
        """Imprime un mensaje de advertencia."""
        color = ConsoleFormatter.COLORS
        print(f"{color['yellow']}⚠️  {message}{color['reset']}")

    @staticmethod
    def print_info(message: str):
        """Imprime un mensaje informativo."""
        color = ConsoleFormatter.COLORS
        print(f"{color['cyan']}ℹ️  {message}{color['reset']}")


def parse_json_response(response_text: str) -> Dict[str, Any]:
    """
    Intenta parsear una respuesta JSON de OpenAI.
    Maneja casos donde la respuesta está envuelta en markdown.
    """
    # Si está envuelto en ```json ... ```, extraer
    if "```json" in response_text:
        start = response_text.find("```json") + 7
        end = response_text.find("```", start)
        response_text = response_text[start:end].strip()
    elif "```" in response_text:
        start = response_text.find("```") + 3
        end = response_text.find("```", start)
        response_text = response_text[start:end].strip()

    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.error(f"Error al parsear JSON: {e}")
        logger.debug(f"Texto original: {response_text}")
        return {"error": "No se pudo parsear la respuesta como JSON"}

