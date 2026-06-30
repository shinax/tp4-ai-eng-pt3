"""
Módulo de agentes para el sistema de comparación de imágenes.
Proporciona agentes reutilizables para lectura y comparación de imágenes.
"""

import base64
from pathlib import Path
from typing import Optional
from langfuse.openai import openai
from langfuse import Langfuse


def parse_contract_image(image_path: str, image_label: str, custom_prompt: Optional[str] = None) -> dict:
    """
    Analiza una imagen de contrato y retorna detalles estructurados.
    
    Args:
        image_path: Ruta a la imagen a analizar
        image_label: Etiqueta para identificar la imagen (ej: "imagen_1", "imagen_2")
        custom_prompt: Prompt personalizado (opcional)
    
    Returns:
        Diccionario con el análisis de la imagen
    """
    # Codificar imagen a base64
    with open(image_path, "rb") as image_file:
        image_base64 = base64.standard_b64encode(image_file.read()).decode("utf-8")
    
    # Obtener tipo MIME
    extension = Path(image_path).suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp"
    }
    image_media_type = media_types.get(extension, "image/jpeg")
    
    # Usar prompt personalizado o por defecto
    if custom_prompt is None:
        custom_prompt = """Analiza esta imagen de contrato/documento de forma detallada. 
            Proporciona:
            1. Descripción general
            2. Objetos principales identificados
            3. Colores predominantes
            4. Texto visible (si lo hay)
            5. Características destacadas
            6. Cualquier marca, sello o firma visible

            Responde en formato JSON."""
    
    # Llamar a OpenAI con capacidad de visión
    response = openai.chat.completions.create(
        name="parse-contract-image",
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": custom_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{image_media_type};base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
    )
    
    analysis = response.choices[0].message.content
    
    return {
        "label": image_label,
        "image_path": image_path,
        "analysis": analysis
    }


class ImageReaderAgent:
    """Agente especializado en leer y analizar imágenes."""
    
    def __init__(self, langfuse_client: Optional[Langfuse] = None):
        self.langfuse_client = langfuse_client or Langfuse()
    
    def analyze(self, image_path_1: str, image_path_2: str, custom_prompt: Optional[str] = None) -> dict:
        """
        Analiza dos imágenes ejecutando parse_contract_image para cada una.
        
        Args:
            image_path_1: Ruta a la primera imagen
            image_path_2: Ruta a la segunda imagen
            custom_prompt: Prompt personalizado (opcional)
        
        Returns:
            Diccionario con el análisis de ambas imágenes
        """
        # Ejecutar parse_contract_image para la primera imagen
        analysis_1 = parse_contract_image(image_path_1, "imagen_1", custom_prompt)
        
        # Ejecutar parse_contract_image para la segunda imagen
        analysis_2 = parse_contract_image(image_path_2, "imagen_2", custom_prompt)
        
        # Combinar análisis
        combined_analysis = {
            "imagen_1": analysis_1["analysis"],
            "imagen_2": analysis_2["analysis"]
        }
        
        return {
            "status": "success",
            "image_1_path": image_path_1,
            "image_2_path": image_path_2,
            "analysis": str(combined_analysis)
        }



class ImageComparatorAgent:
    """Agente especializado en comparar análisis de imágenes."""
    
    def __init__(self, langfuse_client: Optional[Langfuse] = None):
        self.langfuse_client = langfuse_client or Langfuse()
    
    def compare(self, analysis_data: dict, custom_prompt: Optional[str] = None) -> dict:
        """
        Compara dos análisis de imágenes para identificar diferencias.
        
        Args:
            analysis_data: Diccionario con el análisis de ambas imágenes
            custom_prompt: Prompt personalizado (opcional)
        
        Returns:
            Diccionario con la comparación detallada
        """
        # Usar prompt personalizado o por defecto
        if custom_prompt is None:
            custom_prompt = f"""Basándote en el siguiente análisis de dos imágenes:

{analysis_data['analysis']}

Por favor, realiza una comparación detallada:
1. **Similitudes**: ¿Qué elementos son comunes entre ambas imágenes?
2. **Diferencias principales**: ¿Cuáles son las diferencias más notables?
3. **Diferencias en detalles**: Diferencias en colores, tamaño, posición, etc.
4. **Análisis contextual**: ¿Qué sugieren estas diferencias?
5. **Conclusiones**: Resumen ejecutivo de las diferencias encontradas

Responde en formato JSON con claves: 'similitudes', 'diferencias_principales', 'diferencias_detalles', 'analisis_contextual', 'conclusiones'."""
        
        # Llamar a OpenAI para la comparación
        response = openai.chat.completions.create(
            name="compare-images",
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un experto en análisis comparativo de imágenes. Proporciona análisis detallados y precisos."
                },
                {
                    "role": "user",
                    "content": custom_prompt
                }
            ]
        )
        
        comparison_result = response.choices[0].message.content
        
        return {
            "status": "success",
            "comparison": comparison_result
        }


class ImageComparisonWorkflow:
    """Orquesta el flujo de comparación de imágenes con dos agentes."""
    
    def __init__(self, langfuse_client: Optional[Langfuse] = None):
        self.langfuse_client = langfuse_client or Langfuse()
        self.reader_agent = ImageReaderAgent(self.langfuse_client)
        self.comparator_agent = ImageComparatorAgent(self.langfuse_client)
    
    def process(
        self,
        image_path_1: str,
        image_path_2: str,
        reader_prompt: Optional[str] = None,
        comparator_prompt: Optional[str] = None
    ) -> dict:
        """
        Ejecuta el flujo completo de comparación de imágenes.
        
        Args:
            image_path_1: Ruta a la primera imagen
            image_path_2: Ruta a la segunda imagen
            reader_prompt: Prompt personalizado para el agente lector (opcional)
            comparator_prompt: Prompt personalizado para el agente comparador (opcional)
        
        Returns:
            Diccionario con los resultados del análisis y comparación
        """
        # Crear un trace ID para toda la sesión
        trace_id = self.langfuse_client.create_trace_id()
        
        # Ejecutar Agente 1
        analysis_result = self.reader_agent.analyze(
            image_path_1,
            image_path_2,
            reader_prompt
        )
        
        if analysis_result["status"] != "success":
            return {"error": "Reader agent failed"}
        
        # Ejecutar Agente 2
        comparison_result = self.comparator_agent.compare(
            analysis_result,
            comparator_prompt
        )
        
        if comparison_result["status"] != "success":
            return {"error": "Comparator agent failed"}
        
        return {
            "status": "success",
            "trace_id": trace_id,
            "image_analysis": analysis_result,
            "image_comparison": comparison_result
        }

