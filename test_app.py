#!/usr/bin/env python3
"""
Script de prueba para el sistema de comparación de imágenes.
Crea imágenes de prueba y ejecuta el análisis completo.
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
    create_test_images,
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
    
    # Crear imágenes de prueba
    ConsoleFormatter.print_header("🧪 PRUEBA DEL SISTEMA DE COMPARACIÓN DE IMÁGENES")
    
    print_workflow_status("init", "Creando imágenes de prueba...")
    if not create_test_images():
        ConsoleFormatter.print_error("No se pudieron crear las imágenes de prueba")
        return False
    ConsoleFormatter.print_success("Imágenes de prueba creadas")
    
    # Verificar que las imágenes existan
    image_1 = "examples/image_1.jpg"
    image_2 = "examples/image_2.jpg"
    
    if not os.path.exists(image_1) or not os.path.exists(image_2):
        ConsoleFormatter.print_error(f"No se encontraron las imágenes de prueba")
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
        
        ConsoleFormatter.print_section("🔄 Comparación de Imágenes (Agente 2: Comparador)")
        print(result["image_comparison"]["comparison"])
        print()
        
        # Guardar resultados
        ConsoleFormatter.print_section("💾 Guardando Resultados")
        
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
