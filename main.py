import os
import base64
import json
from pathlib import Path
from dotenv import load_dotenv
from langfuse.openai import openai
from langfuse import Langfuse

# Load environment variables
load_dotenv()

# Initialize Langfuse for tracing
langfuse_client = Langfuse()


def encode_image_to_base64(image_path: str) -> str:
    """Encodes an image file to base64 string for API consumption."""
    with open(image_path, "rb") as image_file:
        return base64.standard_b64encode(image_file.read()).decode("utf-8")


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


def agent_read_images(image_path_1: str, image_path_2: str, trace_name: str = "read-images") -> dict:
    """
    Agent 1: Reads and analyzes two images.
    Returns detailed descriptions of each image.
    """
    with langfuse_client.trace(
        name=trace_name,
        metadata={"agent": "image_reader", "images": [image_path_1, image_path_2]}
    ) as trace:
        
        # Encode images to base64
        trace.generation(
            name="encode_images",
            input={
                "image_1": image_path_1,
                "image_2": image_path_2
            }
        )
        
        image1_base64 = encode_image_to_base64(image_path_1)
        image1_media_type = get_image_media_type(image_path_1)
        
        image2_base64 = encode_image_to_base64(image_path_2)
        image2_media_type = get_image_media_type(image_path_2)
        
        # Call OpenAI with vision capability
        trace.generation(
            name="analyze_images",
            input="Analyzing two images"
        )
        
        response = openai.chat.completions.create(
            name="agent-read-images",
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analiza estas dos imágenes de forma detallada. 
                            Para cada imagen, proporciona:
                            1. Descripción general
                            2. Objetos principales identificados
                            3. Colores predominantes
                            4. Texto visible (si lo hay)
                            5. Características destacadas
                            
                            Responde en formato JSON con claves 'imagen_1' e 'imagen_2'."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{image1_media_type};base64,{image1_base64}"
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{image2_media_type};base64,{image2_base64}"
                            }
                        }
                    ]
                }
            ]
        )
        
        # Parse the response
        analysis = response.choices[0].message.content
        
        trace.generation(
            name="parse_analysis",
            output=analysis
        )
        
        return {
            "status": "success",
            "image_1_path": image_path_1,
            "image_2_path": image_path_2,
            "analysis": analysis
        }


def agent_compare_images(image_analysis: dict, trace_name: str = "compare-images") -> dict:
    """
    Agent 2: Compares the analysis from Agent 1.
    Identifies similarities, differences, and provides insights.
    """
    with langfuse_client.trace(
        name=trace_name,
        metadata={"agent": "image_comparator"}
    ) as trace:
        
        trace.generation(
            name="extract_analysis",
            input=image_analysis
        )
        
        # Prepare the comparison prompt
        comparison_prompt = f"""Basándote en el siguiente análisis de dos imágenes:

{image_analysis['analysis']}

Por favor, realiza una comparación detallada:
1. **Similitudes**: ¿Qué elementos son comunes entre ambas imágenes?
2. **Diferencias principales**: ¿Cuáles son las diferencias más notables?
3. **Diferencias en detalles**: Diferencias en colores, tamaño, posición, etc.
4. **Análisis contextual**: ¿Qué sugieren estas diferencias?
5. **Conclusiones**: Resumen ejecutivo de las diferencias encontradas

Responde en formato JSON con claves: 'similitudes', 'diferencias_principales', 'diferencias_detalles', 'analisis_contextual', 'conclusiones'."""
        
        trace.generation(
            name="compare_analysis",
            input=comparison_prompt
        )
        
        # Call OpenAI for comparison
        response = openai.chat.completions.create(
            name="agent-compare-images",
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un experto en análisis comparativo de imágenes. Proporciona análisis detallados y precisos."
                },
                {
                    "role": "user",
                    "content": comparison_prompt
                }
            ]
        )
        
        comparison_result = response.choices[0].message.content
        
        trace.generation(
            name="parse_comparison",
            output=comparison_result
        )
        
        return {
            "status": "success",
            "comparison": comparison_result
        }


def process_image_comparison(image_path_1: str, image_path_2: str) -> dict:
    """
    Orchestrates the two-agent workflow:
    1. Agent 1 reads and analyzes both images
    2. Agent 2 compares the analysis and finds differences
    """
    # Create a main trace for the entire workflow
    with langfuse_client.trace(
        name="image-comparison-workflow",
        metadata={
            "workflow": "two-agent-image-comparison",
            "images": [image_path_1, image_path_2]
        }
    ) as main_trace:
        
        # Step 1: Agent 1 - Read and analyze images
        main_trace.event(
            name="workflow_started",
            input={
                "image_1": image_path_1,
                "image_2": image_path_2
            }
        )
        
        print("🔍 Agente 1: Leyendo y analizando imágenes...")
        analysis_result = agent_read_images(image_path_1, image_path_2)
        
        if analysis_result["status"] != "success":
            return {"error": "Agent 1 failed"}
        
        # Step 2: Agent 2 - Compare analysis
        print("🔄 Agente 2: Comparando imágenes...")
        comparison_result = agent_compare_images(analysis_result)
        
        if comparison_result["status"] != "success":
            return {"error": "Agent 2 failed"}
        
        main_trace.event(
            name="workflow_completed",
            output={
                "analysis": analysis_result["analysis"],
                "comparison": comparison_result["comparison"]
            }
        )
        
        return {
            "status": "success",
            "image_analysis": analysis_result,
            "image_comparison": comparison_result
        }


def main():
    """Main function to demonstrate the two-agent workflow."""
    
    # Example usage - you can replace these with actual image paths
    # For testing, we'll create sample images or use URLs
    
    print("=" * 60)
    print("🚀 Aplicación de Comparación de Imágenes con Agentes IA")
    print("=" * 60)
    print()
    
    # Example 1: Using local image files
    image_1 = "image_1.jpg"  # Replace with your image path
    image_2 = "image_2.jpg"  # Replace with your image path
    
    # Check if images exist
    if not os.path.exists(image_1) or not os.path.exists(image_2):
        print("⚠️  Por favor, proporciona dos archivos de imagen:")
        print(f"   - {image_1}")
        print(f"   - {image_2}")
        print()
        print("📝 Ejemplo de uso:")
        print("   python main.py --image1 path/to/image1.jpg --image2 path/to/image2.jpg")
        return
    
    # Process the images
    result = process_image_comparison(image_1, image_2)
    
    print()
    print("=" * 60)
    print("📊 RESULTADOS")
    print("=" * 60)
    print()
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print("✅ Análisis de Imágenes (Agente 1):")
        print("-" * 60)
        print(result["image_analysis"]["analysis"])
        print()
        print("✅ Comparación de Imágenes (Agente 2):")
        print("-" * 60)
        print(result["image_comparison"]["comparison"])
        print()
    
    # Flush Langfuse traces
    langfuse_client.flush()
    print("📡 Trazas enviadas a Langfuse")


if __name__ == "__main__":
    main()
