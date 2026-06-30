#!/usr/bin/env python3
"""
Script de ejemplo para probar el sistema de comparación de imágenes.
Descarga imágenes de ejemplo y ejecuta el análisis completo.
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from langfuse import Langfuse
from agents import ImageComparisonWorkflow
from utils import (
    ConsoleFormatter, 
    ResultSaver, 
    create_test_images,
    print_workflow_status
)
from config import validate_configuration

# Load environment variables
load_dotenv()

# Initialize Langfuse
langfuse_client = Langfuse()


def download_example_images():
    """Descarga imágenes de ejemplo para las pruebas."""
    print("📥 Descargando imágenes de ejemplo...")
    
    import urllib.request
    
    # Crear directorio de ejemplos
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)
    
    # Imágenes de ejemplo (deberías reemplazar estos URLs con imágenes reales)
    # Para demostración, usaremos imágenes públicas de ejemplo
    
    print("   ℹ️  Nota: Por favor, coloca dos imágenes en el directorio 'examples/'")
    print("   ℹ️  Ejemplo:")
    print("       - examples/image_1.jpg")
    print("       - examples/image_2.jpg")
    return False


def demonstrate_workflow(image_1: str, image_2: str, custom_reader_prompt: str = None, custom_comparator_prompt: str = None):
    """Demuestra el flujo completo de análisis y comparación."""
    
    # Validar que las imágenes existan
    if not os.path.exists(image_1):
        print(f"❌ Error: No se encontró {image_1}")
        return
    
    if not os.path.exists(image_2):
        print(f"❌ Error: No se encontró {image_2}")
        return
    
    print("\n" + "=" * 70)
    print("🚀 SISTEMA DE COMPARACIÓN DE IMÁGENES CON AGENTES IA")
    print("=" * 70)
    print()
    
    print(f"📷 Imagen 1: {image_1}")
    print(f"📷 Imagen 2: {image_2}")
    print()
    
    # Crear el flujo
    workflow = ImageComparisonWorkflow(langfuse_client)
    
    print("⏳ Procesando imágenes...")
    print()
    
    # Ejecutar el análisis
    result = workflow.process(
        image_1,
        image_2,
        reader_prompt=custom_reader_prompt,
        comparator_prompt=custom_comparator_prompt
    )
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    # Mostrar resultados
    print("=" * 70)
    print("✅ ANÁLISIS DE IMÁGENES (Agente 1: Lector)")
    print("=" * 70)
    print()
    print(result["image_analysis"]["analysis"])
    print()
    
    print("=" * 70)
    print("✅ COMPARACIÓN DE IMÁGENES (Agente 2: Comparador)")
    print("=" * 70)
    print()
    print(result["image_comparison"]["comparison"])
    print()
    
    # Mostrar información de Langfuse
    print("=" * 70)
    print("📡 INFORMACIÓN DE TRAZAS")
    print("=" * 70)
    print()
        
    # Guardar en JSON
    result_to_save = {
        "image_analysis": result["image_analysis"],
        "image_comparison": result["image_comparison"]
    }
    
    json_path = ResultSaver.save_json(result_to_save)
    print(f"  ✓ JSON: {json_path.name}")
    
    # Guardar en Markdown
    md_path = ResultSaver.save_markdown(
        result["image_analysis"]["analysis"],
        result["image_comparison"]["comparison"]
    )
    print(f"  ✓ Markdown: {md_path.name}")
    
    env_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    if env_public_key:
        project_id = env_public_key.split("-")[-1] if "-" in env_public_key else env_public_key
        print(f"✅ Trazas enviadas a Langfuse")
        print(f"   Project ID: {project_id}")
        print(f"   Dashboard: https://cloud.langfuse.com")
    else:
        print("⚠️  LANGFUSE_PUBLIC_KEY no configurada")
    print()
    
    # Flush traces
    langfuse_client.flush()


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Sistema de comparación de imágenes con agentes IA"
    )
    
    parser.add_argument(
        "--image1",
        type=str,
        required=True,
        help="Ruta a la primera imagen"
    )
    
    parser.add_argument(
        "--image2",
        type=str,
        required=True,
        help="Ruta a la segunda imagen"
    )
    
    parser.add_argument(
        "--reader-prompt",
        type=str,
        default=None,
        help="Prompt personalizado para el agente lector (opcional)"
    )
    
    parser.add_argument(
        "--comparator-prompt",
        type=str,
        default=None,
        help="Prompt personalizado para el agente comparador (opcional)"
    )
    
    parser.add_argument(
        "--download-examples",
        action="store_true",
        help="Descargar imágenes de ejemplo"
    )
    
    args = parser.parse_args()
    
    # Descargar ejemplos si se solicita
    if args.download_examples:
        download_example_images()
        return
    
    # Ejecutar el análisis
    demonstrate_workflow(
        args.image1,
        args.image2,
        args.reader_prompt,
        args.comparator_prompt
    )


if __name__ == "__main__":
    # Si no hay argumentos, mostrar ayuda
    if len(sys.argv) == 1:
        print("📝 Uso:")
        print()
        print("   python example.py --image1 <path> --image2 <path>")
        print()
        print("💡 Ejemplo:")
        print()
        print("   python example.py --image1 examples/image_1.jpg --image2 examples/image_2.jpg")
        print()
        print("Para más opciones, usa: python example.py --help")
        print()
    else:
        main()
