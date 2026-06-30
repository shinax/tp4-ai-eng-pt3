#!/usr/bin/env python3
"""
Script de ejemplo para probar el sistema de análisis de contratos.
Ejecuta el análisis completo con imágenes de la carpeta examples/.
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
    print_workflow_status
)
from config import validate_configuration

# Load environment variables
load_dotenv()

# Initialize Langfuse
langfuse_client = Langfuse()


def demonstrate_workflow(image_1: str, image_2: str, custom_reader_prompt: str = None, custom_text_extractor_prompt: str = None):
    """Demuestra el flujo completo de análisis y comparación."""
    
    # Validar que las imágenes existan
    if not os.path.exists(image_1):
        print(f"❌ Error: No se encontró {image_1}")
        return
    
    if not os.path.exists(image_2):
        print(f"❌ Error: No se encontró {image_2}")
        return
    
    print("\n" + "=" * 70)
    print("🚀 SISTEMA DE ANÁLISIS DE CONTRATOS CON AGENTES IA")
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
        text_extractor_prompt=custom_text_extractor_prompt
    )
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    # Mostrar resultados
    print("=" * 70)
    print("✅ ANÁLISIS DE ESTRUCTURA (Agente 1: Lector)")
    print("=" * 70)
    print()
    print(result["image_analysis"]["analysis"])
    print()
    
    print("=" * 70)
    print("📊 MAPA CONTEXTUAL (Agente 2: Contextualizador)")
    print("=" * 70)
    print()
    print(result["context_map"]["context_map"])
    print()
    
    print("=" * 70)
    print("📄 TEXTO EXTRAÍDO (Agente 3: Extractor de Texto)")
    print("=" * 70)
    print()
    print("--- CONTRATO 1 ---")
    print()
    print(result["extracted_text"]["text_1"])
    print()
    print("--- CONTRATO 2 ---")
    print()
    print(result["extracted_text"]["text_2"])
    print()
    
    print("=" * 70)
    print("🔍 CAMBIOS IDENTIFICADOS (Agente 4: Extractor de Cambios)")
    print("=" * 70)
    print()
    
    if "extracted_changes" in result:
        changes = result["extracted_changes"]
        
        if changes["status"] == "success" or changes["status"] == "validation_error":
            changes_data = changes.get("changes", {})
            
            # Mostrar resumen general de cambios
            if isinstance(changes_data, dict):
                summary = changes_data.get("summary_of_the_change", "")
                sections = changes_data.get("sections_changed", [])
                topics = changes_data.get("topics_touched", [])
                
                if summary:
                    print("📋 RESUMEN EJECUTIVO DE CAMBIOS")
                    print("-" * 70)
                    print(f"{summary}")
                    print()
                
                if sections:
                    print("📍 SECCIONES MODIFICADAS")
                    print("-" * 70)
                    for section in sections:
                        print(f"  • {section}")
                    print()
                
                if topics:
                    print("🏷️  TÓPICOS LEGALES/COMERCIALES AFECTADOS")
                    print("-" * 70)
                    for topic in topics:
                        print(f"  • {topic}")
                    print()
            
            if changes["status"] == "validation_error":
                print(f"⚠️  Nota: Cambios extraídos pero con validación parcial")
                print(f"Error: {changes.get('error', 'Desconocido')}")
                print()
        else:
            print(f"❌ Error al extraer cambios: {changes.get('error', 'Desconocido')}")
            print()
    
    # Mostrar información de Langfuse
    print("=" * 70)
    print("📡 INFORMACIÓN DE TRAZAS")
    print("=" * 70)
    print()
    
    # Guardar en JSON
    result_to_save = {
        "image_analysis": result["image_analysis"],
        "context_map": result["context_map"],
        "extracted_text": result["extracted_text"],
        "extracted_changes": result.get("extracted_changes", {})
    }
    
    json_path = ResultSaver.save_json(result_to_save)
    print(f"  ✓ JSON: {json_path.name}")
    
    # Guardar en Markdown
    md_path = ResultSaver.save_markdown(
        result["image_analysis"]["analysis"],
        result["extracted_text"]["text_1"]
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
        "--text-extractor-prompt",
        type=str,
        default=None,
        help="Prompt personalizado para el agente extractor de texto (opcional)"
    )
    
    args = parser.parse_args()
    
    # Ejecutar el análisis
    demonstrate_workflow(
        args.image1,
        args.image2,
        args.reader_prompt,
        args.text_extractor_prompt
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
