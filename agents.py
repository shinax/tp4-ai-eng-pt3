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



class TextExtractorAgent:
    """Agente especializado en extraer texto completo de imágenes de contratos."""
    
    def __init__(self, langfuse_client: Optional[Langfuse] = None):
        self.langfuse_client = langfuse_client or Langfuse()
    
    def extract_text(self, image_path_1: str, image_path_2: str, custom_prompt: Optional[str] = None) -> dict:
        """
        Extrae el texto completo de dos imágenes de contrato usando vision.
        
        Args:
            image_path_1: Ruta a la primera imagen
            image_path_2: Ruta a la segunda imagen
            custom_prompt: Prompt personalizado (opcional)
        
        Returns:
            Diccionario con el texto extraído de ambos contratos
        """
        # Usar prompt personalizado o por defecto
        if custom_prompt is None:
            custom_prompt = """Extrae el texto COMPLETO del contrato/documento de esta imagen de forma fiel y precisa.
            
            Requisitos:
            1. Captura TODO el texto visible, manteniendo la estructura original
            2. Preserva párrafos, listas numeradas y viñetas
            3. Incluye títulos de secciones y subsecciones
            4. Mantén la puntuación y formato original
            5. Si hay tablas, representa su estructura con separadores claros
            6. Si hay texto parcialmente legible, indica con [texto parcial] o [ilegible]

            Responde SOLO con el texto extraído, sin comentarios adicionales."""
        
        # Extraer texto de la primera imagen
        with open(image_path_1, "rb") as image_file:
            image_1_base64 = base64.standard_b64encode(image_file.read()).decode("utf-8")
        
        extension_1 = Path(image_path_1).suffix.lower()
        media_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        media_type_1 = media_types.get(extension_1, "image/jpeg")
        
        response_1 = openai.chat.completions.create(
            name="extract-contract-text-1",
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
                                "url": f"data:{media_type_1};base64,{image_1_base64}"
                            }
                        }
                    ]
                }
            ]
        )
        
        text_1 = response_1.choices[0].message.content
        
        # Extraer texto de la segunda imagen
        with open(image_path_2, "rb") as image_file:
            image_2_base64 = base64.standard_b64encode(image_file.read()).decode("utf-8")
        
        extension_2 = Path(image_path_2).suffix.lower()
        media_type_2 = media_types.get(extension_2, "image/jpeg")
        
        response_2 = openai.chat.completions.create(
            name="extract-contract-text-2",
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
                                "url": f"data:{media_type_2};base64,{image_2_base64}"
                            }
                        }
                    ]
                }
            ]
        )
        
        text_2 = response_2.choices[0].message.content
        
        return {
            "status": "success",
            "text_1": text_1,
            "text_2": text_2
        }


class ContextualizationAgent:
    """Agente especializado en analizar y mapear la estructura contextual de documentos."""
    
    def __init__(self, langfuse_client: Optional[Langfuse] = None):
        self.langfuse_client = langfuse_client or Langfuse()
    
    def build_context_map(self, analysis_1: str, analysis_2: str, custom_prompt: Optional[str] = None) -> dict:
        """
        Analiza la estructura comparada de dos documentos y construye un mapa contextual.
        
        Args:
            analysis_1: Análisis parseado del primer documento
            analysis_2: Análisis parseado del segundo documento
            custom_prompt: Prompt personalizado (opcional)
        
        Returns:
            Diccionario con el mapa contextual estructurado
        """
        # Usar prompt personalizado o por defecto
        if custom_prompt is None:
            custom_prompt = f"""Analiza la estructura comparada de estos dos documentos.

DOCUMENTO 1:
{analysis_1}

DOCUMENTO 2:
{analysis_2}

Por favor, realiza un análisis ESTRUCTURAL (no de cambios):
1. **Secciones en Documento 1**: Lista las secciones principales identificadas
2. **Secciones en Documento 2**: Lista las secciones principales identificadas
3. **Correspondencias**: Para cada sección, identifica su equivalente en el otro documento
4. **Propósito de bloques**: Explica el propósito general de cada bloque/sección
5. **Estructura comparada**: Cómo se alinean las estructuras entre documentos
6. **Cambios estructurales**: Solo si hay reordenamiento o reorganización de secciones

IMPORTANTE: Este análisis es sobre ESTRUCTURA y CONTEXTO, no sobre cambios de contenido.

Responde en formato JSON con la siguiente estructura:
{{
    "documento_1": {{
        "secciones": [lista de secciones],
        "propósito_general": "..."
    }},
    "documento_2": {{
        "secciones": [lista de secciones],
        "propósito_general": "..."
    }},
    "correspondencias": [mapeo de secciones],
    "análisis_contextual": {{
        "propósito_por_bloque": {{}},
        "cambios_estructurales": "..."
    }},
    "mapa_de_relaciones": "descripción de cómo se relacionan las estructuras"
}}"""
        
        # Llamar a OpenAI para el análisis contextual
        response = openai.chat.completions.create(
            name="build-context-map",
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un experto en análisis de estructura de documentos. Tu tarea es identificar la estructura, secciones y contexto de documentos para construir mapas conceptuales. No analices cambios de contenido, solo estructura y correspondencias."
                },
                {
                    "role": "user",
                    "content": custom_prompt
                }
            ]
        )
        
        context_map = response.choices[0].message.content
        
        return {
            "status": "success",
            "context_map": context_map
        }



class ImageComparisonWorkflow:
    """Orquesta el flujo de comparación de imágenes con tres agentes."""
    
    def __init__(self, langfuse_client: Optional[Langfuse] = None):
        self.langfuse_client = langfuse_client or Langfuse()
        self.reader_agent = ImageReaderAgent(self.langfuse_client)
        self.contextualization_agent = ContextualizationAgent(self.langfuse_client)
        self.text_extractor_agent = TextExtractorAgent(self.langfuse_client)
    
    def process(
        self,
        image_path_1: str,
        image_path_2: str,
        reader_prompt: Optional[str] = None,
        contextualization_prompt: Optional[str] = None,
        text_extractor_prompt: Optional[str] = None
    ) -> dict:
        """
        Ejecuta el flujo completo de análisis con tres agentes:
        1. Agente Lector: Analiza la estructura de ambos documentos
        2. Agente Contextualizador: Mapea la estructura comparada
        3. Agente Extractor de Texto: Extrae el texto completo de forma fiel
        
        Args:
            image_path_1: Ruta a la primera imagen
            image_path_2: Ruta a la segunda imagen
            reader_prompt: Prompt personalizado para el agente lector (opcional)
            contextualization_prompt: Prompt personalizado para contextualizador (opcional)
            text_extractor_prompt: Prompt personalizado para extractor de texto (opcional)
        
        Returns:
            Diccionario con los resultados de todos los agentes
        """
        # Crear un trace ID para toda la sesión
        trace_id = self.langfuse_client.create_trace_id()
        
        # Paso 1: Agente Lector - Analizar ambas imágenes
        analysis_result = self.reader_agent.analyze(
            image_path_1,
            image_path_2,
            reader_prompt
        )
        
        if analysis_result["status"] != "success":
            return {"error": "Reader agent failed"}
        
        # Extraer análisis individuales para pasar al siguiente agente
        import json
        try:
            analysis_dict = eval(analysis_result["analysis"])
            analysis_1 = analysis_dict.get("imagen_1", "")
            analysis_2 = analysis_dict.get("imagen_2", "")
        except:
            analysis_1 = analysis_result["analysis"]
            analysis_2 = analysis_result["analysis"]
        
        # Paso 2: Agente Contextualizador - Construir mapa contextual
        contextualization_result = self.contextualization_agent.build_context_map(
            analysis_1,
            analysis_2,
            contextualization_prompt
        )
        
        if contextualization_result["status"] != "success":
            return {"error": "Contextualization agent failed"}
        
        # Paso 3: Agente Extractor de Texto - Extraer texto completo de contratos
        text_extraction_result = self.text_extractor_agent.extract_text(
            image_path_1,
            image_path_2,
            text_extractor_prompt
        )
        
        if text_extraction_result["status"] != "success":
            return {"error": "Text extractor agent failed"}
        
        return {
            "status": "success",
            "trace_id": trace_id,
            "image_analysis": analysis_result,
            "context_map": contextualization_result,
            "extracted_text": text_extraction_result
        }

