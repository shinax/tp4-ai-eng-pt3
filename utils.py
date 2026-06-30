"""
Utilidades para la aplicación de comparación de imágenes.
"""

import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime
from pathlib import Path
import sys

from config import LOG_LEVEL, OUTPUT_DIR


# Configurar logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class ResultFormatter:
    """Formatea los resultados para diferentes salidas."""
    
    @staticmethod
    def to_json(data: Any) -> str:
        """Convierte datos a JSON formateado."""
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    @staticmethod
    def to_markdown(analysis: str, comparison: str) -> str:
        """Convierte resultados a formato Markdown."""
        return f"""# Resultados de Comparación de Imágenes

## Análisis de Imágenes

{analysis}

## Comparación de Imágenes

{comparison}

---
*Generado en: {datetime.now().isoformat()}*
"""
    
    @staticmethod
    def to_text(analysis: str, comparison: str) -> str:
        """Convierte resultados a texto plano."""
        return f"""RESULTADOS DE COMPARACIÓN DE IMÁGENES
{'=' * 50}

ANÁLISIS DE IMÁGENES:
{'-' * 50}
{analysis}

COMPARACIÓN DE IMÁGENES:
{'-' * 50}
{comparison}

Generado en: {datetime.now().isoformat()}
"""


class ResultSaver:
    """Guarda los resultados en archivos."""
    
    @staticmethod
    def save_json(data: Dict[str, Any], filename: Optional[str] = None) -> Path:
        """Guarda resultados en formato JSON."""
        if filename is None:
            filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = OUTPUT_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Resultados guardados en: {filepath}")
        return filepath
    
    @staticmethod
    def save_markdown(analysis: str, comparison: str, filename: Optional[str] = None) -> Path:
        """Guarda resultados en formato Markdown."""
        if filename is None:
            filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        filepath = OUTPUT_DIR / filename
        content = ResultFormatter.to_markdown(analysis, comparison)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Resultados guardados en: {filepath}")
        return filepath
    
    @staticmethod
    def save_text(analysis: str, comparison: str, filename: Optional[str] = None) -> Path:
        """Guarda resultados en formato texto."""
        if filename is None:
            filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        filepath = OUTPUT_DIR / filename
        content = ResultFormatter.to_text(analysis, comparison)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Resultados guardados en: {filepath}")
        return filepath


class ConsoleFormatter:
    """Formatea la salida para consola."""
    
    # Colores ANSI
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
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


def print_workflow_status(stage: str, status: str, details: Optional[str] = None):
    """Imprime el estado del flujo de trabajo."""
    stages = {
        "init": "🚀",
        "reading": "📖",
        "analyzing": "🔍",
        "comparing": "🔄",
        "processing": "⏳",
        "complete": "✅",
        "error": "❌",
    }
    
    emoji = stages.get(stage, "•")
    color = ConsoleFormatter.COLORS
    
    if status == "processing":
        message = f"{emoji} {stage}: {status}"
        print(message, end='\r', flush=True)
    else:
        print(f"{emoji} {stage}: {status}")
        if details:
            print(f"   └─ {details}")


# Test utilities
def create_test_images():
    """Crea imágenes de prueba para testing."""
    try:
        from PIL import Image, ImageDraw
        
        examples_dir = Path("examples")
        examples_dir.mkdir(exist_ok=True)
        
        # Crear imagen 1: Rectángulo azul
        img1 = Image.new('RGB', (400, 300), color='white')
        draw1 = ImageDraw.Draw(img1)
        draw1.rectangle([50, 50, 350, 250], fill='blue', outline='black', width=2)
        draw1.text((150, 130), "Imagen 1", fill='white')
        img1.save(examples_dir / "image_1.jpg")
        
        # Crear imagen 2: Rectángulo rojo
        img2 = Image.new('RGB', (400, 300), color='white')
        draw2 = ImageDraw.Draw(img2)
        draw2.rectangle([50, 50, 350, 250], fill='red', outline='black', width=2)
        draw2.text((150, 130), "Imagen 2", fill='white')
        img2.save(examples_dir / "image_2.jpg")
        
        logger.info("Imágenes de prueba creadas exitosamente")
        return True
    except ImportError:
        logger.error("Pillow no está instalada. Instala con: pip install Pillow")
        return False
    except Exception as e:
        logger.error(f"Error al crear imágenes de prueba: {e}")
        return False
