#!/usr/bin/env python3
"""
Script de prueba para el sistema de análisis de contratos.
Ejecuta el análisis completo usando imágenes de la carpeta examples/.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import after load_dotenv
from langfuse import Langfuse
from agents import ImageComparisonWorkflow
from utils import (
    ConsoleFormatter, 
    ResultSaver, 
    print_workflow_status
)
from config import validate_configuration


def run_test():
    """Ejecuta la prueba completa."""
    
    # Validar configuración
    config = validate_configuration()
    
    if not config["is_valid"]:
        ConsoleFormatter.print_error("Configuración inválida")
        for error in config["errors"]:
            ConsoleFormatter.print_error(f"  - {error}")
        return False
    
    for warning in config["warnings"]:
        ConsoleFormatter.print_warning(f"  {warning}")
    
    # Usar imágenes de la carpeta examples
    ConsoleFormatter.print_header("🧪 PRUEBA DEL SISTEMA DE COMPARACIÓN DE IMÁGENES")
    
    # Verificar que las imágenes existan
    image_1 = "examples/image_1.jpg"
    image_2 = "examples/image_2.jpg"
    
    if not os.path.exists(image_1) or not os.path.exists(image_2):
        ConsoleFormatter.print_error(f"No se encontraron imágenes en la carpeta examples/")
        ConsoleFormatter.print_info(f"Por favor, coloca dos imágenes JPG en examples/")
        ConsoleFormatter.print_info(f"  - examples/image_1.jpg")
        ConsoleFormatter.print_info(f"  - examples/image_2.jpg")
        return False
    
    # Inicializar Langfuse
    print_workflow_status("init", "Inicializando Langfuse...")
    langfuse_client = Langfuse()
    ConsoleFormatter.print_success("Langfuse inicializado")
    
    # Crear flujo de trabajo
    print_workflow_status("init", "Inicializando agentes...")
    workflow = ImageComparisonWorkflow(langfuse_client)
    ConsoleFormatter.print_success("Agentes inicializados")
    
    print()
    ConsoleFormatter.print_section("📊 Configuración de Prueba")
    print(f"  Imagen 1: {image_1}")
    print(f"  Imagen 2: {image_2}")
    print()
    
    # Ejecutar el análisis
    print_workflow_status("processing", "Ejecutando análisis...", "Agente 1 (Lector)")
    
    try:
        result = workflow.process(image_1, image_2)
        
        if "error" in result:
            ConsoleFormatter.print_error(f"Error en el análisis: {result['error']}")
            return False
        
        # Mostrar resultados
        ConsoleFormatter.print_header("✅ RESULTADOS DEL ANÁLISIS")
        
        ConsoleFormatter.print_section("📖 Análisis de Imágenes (Agente 1: Lector)")
        print(result["image_analysis"]["analysis"])
        print()
        
        ConsoleFormatter.print_section("� Mapa Contextual (Agente 2: Contextualizador)")
        print(result["context_map"]["context_map"])
        print()
        
        ConsoleFormatter.print_section("� Mapa Contextual (Agente 2: Contextualizador)")
        print(result["context_map"]["context_map"])
        print()
        
        ConsoleFormatter.print_section("📄 Texto Extraído (Agente 3: Extractor de Texto)")
        print("--- CONTRATO 1 ---")
        print()
        print(result["extracted_text"]["text_1"])
        print()
        print("--- CONTRATO 2 ---")
        print()
        print(result["extracted_text"]["text_2"])
        print()
        
        # Guardar resultados
        ConsoleFormatter.print_section("💾 Guardando Resultados")
        
        # Guardar en JSON
        result_to_save = {
            "image_analysis": result["image_analysis"],
            "context_map": result["context_map"],
            "extracted_text": result["extracted_text"]
        }
        
        json_path = ResultSaver.save_json(result_to_save)
        print(f"  ✓ JSON: {json_path.name}")
        
        # Guardar en Markdown
        md_path = ResultSaver.save_markdown(
            result["image_analysis"]["analysis"],
            result["extracted_text"]["text_1"]
        )
        print(f"  ✓ Markdown: {md_path.name}")
        
        print()
        
        # Información de Langfuse
        ConsoleFormatter.print_section("📡 Información de Trazas")
        langfuse_client.flush()
        
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        if public_key:
            ConsoleFormatter.print_success("Trazas enviadas a Langfuse")
            project_id = public_key.split("-")[-1] if "-" in public_key else public_key
            print(f"  Project ID: {project_id}")
            print(f"  Dashboard: https://cloud.langfuse.com")
        else:
            ConsoleFormatter.print_warning("Trazas no enviadas (LANGFUSE_PUBLIC_KEY no configurada)")
        
        print()
        ConsoleFormatter.print_header("✨ PRUEBA COMPLETADA EXITOSAMENTE")
        
        return True
        
    except Exception as e:
        ConsoleFormatter.print_error(f"Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
