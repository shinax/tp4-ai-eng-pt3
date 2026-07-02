"""
Módulo de agentes para el sistema de comparación de imágenes.
Proporciona agentes reutilizables para lectura y comparación de imágenes.
"""

import base64
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from langfuse.openai import openai
from langfuse import Langfuse
from pydantic import BaseModel, Field


# Modelos Pydantic para validación de cambios
class Change(BaseModel):
    """Modelo para un cambio específico"""
    section: str = Field(..., description="Sección donde ocurre el cambio")
    description: str = Field(..., description="Descripción detallada del cambio")
    original_text: Optional[str] = Field(None, description="Texto original (para eliminaciones y modificaciones)")
    new_text: Optional[str] = Field(None, description="Texto nuevo (para adiciones y modificaciones)")
    context: Optional[str] = Field(None, description="Contexto del cambio para mayor claridad")


class ContractChangeOutput(BaseModel):
    """Modelo para el output validado del ChangeExtractorAgent"""
    sections_changed: List[str] = Field(default_factory=list, description="Identificadores únicos de secciones modificadas (ej: 1, 2, 3, 7)")
    topics_touched: List[str] = Field(default_factory=list, description="Categorías legales/comerciales afectadas (ej: Plazo, Pago, Responsabilidad, etc.)")
    summary_of_the_change: str = Field(default="", description="Descripción detallada y comprehensiva de todos los cambios realizados en la enmienda")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sections_changed": ["1", "2", "3", "4", "5", "7"],
                "topics_touched": ["Alcance de Licencia", "Plazo", "Pago", "Soporte", "Terminación", "Protección de Datos"],
                "summary_of_the_change": "La enmienda modifica términos clave del contrato incluyendo: extensión de plazo (12→24 meses), aumento de tarifa (USD 12K→15K), adición de soporte vía chat, ampliación del alcance de uso, extensión del período de terminación (30→60 días), y agregación de cláusula de protección de datos."
            }
        }


def parse_contract_image(image_path: str, image_label: str, custom_prompt: Optional[str] = None, trace_id: Optional[str] = None, langfuse_client: Optional[Langfuse] = None) -> dict:
    """
    Analiza una imagen de contrato y retorna detalles estructurados.
    
    Args:
        image_path: Ruta a la imagen a analizar
        image_label: Etiqueta para identificar la imagen (ej: "imagen_1", "imagen_2")
        custom_prompt: Prompt personalizado (opcional)
        trace_id: ID del trace de Langfuse (opcional)
        langfuse_client: Cliente de Langfuse (opcional)
    
    Returns:
        Diccionario con el análisis de la imagen
    """
    langfuse_client = langfuse_client or Langfuse()
    # Span: Cargar y preparar imagen
    trace_context = {"trace_id": trace_id} if trace_id else None
    with langfuse_client.start_as_current_observation(
        trace_context=trace_context,
        name=f"load-image-{image_label}",
        as_type="span",
        input={"image_path": image_path, "image_label": image_label},
        metadata={"type": "image_preparation"}
    ) as span:
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
        span.update(output={"media_type": image_media_type, "size": len(image_base64)})
    
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
    
    # Span: Análisis de imagen con GPT-4o vision
    with langfuse_client.start_as_current_observation(
        trace_context=trace_context,
        name=f"analyze-image-{image_label}",
        as_type="span",
        input={"image_label": image_label, "prompt_length": len(custom_prompt)},
        metadata={"type": "vision_analysis", "model": "gpt-4o"}
    ) as span:
        # Llamar a OpenAI con capacidad de visión
        response = openai.chat.completions.create(
            name=f"parse-contract-image-{image_label}",
            trace_id=trace_id,
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
        span.update(output={"analysis_length": len(analysis), "model": "gpt-4o"})
    
    return {
        "label": image_label,
        "image_path": image_path,
        "analysis": analysis
    }


class ImageReaderAgent:
    """Agente especializado en leer y analizar imágenes."""
    
    def __init__(self, langfuse_client: Optional[Langfuse] = None):
        self.langfuse_client = langfuse_client or Langfuse()
    
    def analyze(self, image_path_1: str, image_path_2: str, custom_prompt: Optional[str] = None, trace_id: Optional[str] = None) -> dict:
        """
        Analiza dos imágenes ejecutando parse_contract_image para cada una.
        
        Args:
            image_path_1: Ruta a la primera imagen
            image_path_2: Ruta a la segunda imagen
            custom_prompt: Prompt personalizado (opcional)
            trace_id: ID del trace de Langfuse (opcional)
        
        Returns:
            Diccionario con el análisis de ambas imágenes
        """
        # Span principal: Análisis de imágenes
        trace_context = {"trace_id": trace_id} if trace_id else None
        with self.langfuse_client.start_as_current_observation(
            trace_context=trace_context,
            name="image-reader-analyze",
            as_type="span",
            input={"image_path_1": image_path_1, "image_path_2": image_path_2},
            metadata={"type": "agent_operation", "agent": "ImageReaderAgent"}
        ) as reader_span:
            # Ejecutar parse_contract_image para la primera imagen
            analysis_1 = parse_contract_image(image_path_1, "imagen_1", custom_prompt, trace_id, self.langfuse_client)
            
            # Ejecutar parse_contract_image para la segunda imagen
            analysis_2 = parse_contract_image(image_path_2, "imagen_2", custom_prompt, trace_id, self.langfuse_client)
            
            reader_span.update(output={"analysis_1_length": len(str(analysis_1)), "analysis_2_length": len(str(analysis_2))})
        
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
    
    def extract_text(self, image_path_1: str, image_path_2: str, custom_prompt: Optional[str] = None, trace_id: Optional[str] = None) -> dict:
        """
        Extrae el texto completo de dos imágenes de contrato usando vision.
        
        Args:
            image_path_1: Ruta a la primera imagen
            image_path_2: Ruta a la segunda imagen
            custom_prompt: Prompt personalizado (opcional)
            trace_id: ID del trace de Langfuse (opcional)
        
        Returns:
            Diccionario con el texto extraído de ambos contratos
        """
        # Span principal: Extracción de texto
        trace_context = {"trace_id": trace_id} if trace_id else None
        with self.langfuse_client.start_as_current_observation(
            trace_context=trace_context,
            name="text-extractor-extract",
            as_type="span",
            input={"image_path_1": image_path_1, "image_path_2": image_path_2},
            metadata={"type": "agent_operation", "agent": "TextExtractorAgent"}
        ) as extractor_span:
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
            
            # Span: Extracción de texto de imagen 1
            with self.langfuse_client.start_as_current_observation(
                trace_context=trace_context,
                name="extract-text-image-1",
                as_type="span",
                input={"image_path": image_path_1},
                metadata={"type": "vision_extraction"}
            ) as span_1:
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
                    trace_id=trace_id,
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
                span_1.update(output={"text_length": len(text_1), "model": "gpt-4o"})
            
            # Span: Extracción de texto de imagen 2
            with self.langfuse_client.start_as_current_observation(
                trace_context=trace_context,
                name="extract-text-image-2",
                as_type="span",
                input={"image_path": image_path_2},
                metadata={"type": "vision_extraction"}
            ) as span_2:
                # Extraer texto de la segunda imagen
                with open(image_path_2, "rb") as image_file:
                    image_2_base64 = base64.standard_b64encode(image_file.read()).decode("utf-8")
                
                extension_2 = Path(image_path_2).suffix.lower()
                media_type_2 = media_types.get(extension_2, "image/jpeg")
                
                response_2 = openai.chat.completions.create(
                    name="extract-contract-text-2",
                    trace_id=trace_id,
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
                span_2.update(output={"text_length": len(text_2), "model": "gpt-4o"})
            
            extractor_span.update(output={"text_1_length": len(text_1), "text_2_length": len(text_2)})
        
            return {
                "status": "success",
                "text_1": text_1,
                "text_2": text_2
            }


class ChangeExtractorAgent:
    """Agente especializado en extraer y clasificar cambios entre dos documentos."""
    
    def __init__(self, langfuse_client: Optional[Langfuse] = None):
        self.langfuse_client = langfuse_client or Langfuse()
    
    def extract_changes(
        self, 
        text_1: str, 
        text_2: str,
        context_map: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> dict:
        """
        Identifica, aísla y describe cada cambio entre dos textos.
        Distingue entre adiciones, eliminaciones y modificaciones.
        
        Args:
            text_1: Texto del documento original
            text_2: Texto del documento con enmienda
            context_map: Mapa contextual del ContextualizationAgent (opcional)
            custom_prompt: Prompt personalizado (opcional)
            trace_id: ID del trace de Langfuse (opcional)
        
        Returns:
            Diccionario con cambios estructurados y validados
        """
        # Usar prompt personalizado o por defecto
        if custom_prompt is None:
            context_section = f"""

MAPA CONTEXTUAL (para referencia):
{context_map}""" if context_map else ""
            
            custom_prompt = f"""Analiza los siguientes dos textos de contrato y extrae un resumen integral de todos los cambios.{context_section}

DOCUMENTO ORIGINAL:
{text_1}

DOCUMENTO CON ENMIENDA:
{text_2}

Por favor, responde ESTRICTAMENTE con un JSON válido que siga esta estructura:
{{
    "sections_changed": ["1", "2", "3"],
    "topics_touched": ["Plazo", "Pago", "Soporte"],
    "summary_of_the_change": "Descripción detallada de todos los cambios realizados..."
}}

INSTRUCCIONES:
1. sections_changed: Lista de identificadores numéricos/alfanuméricos de TODAS las secciones afectadas (ej: "1", "2.1", "7", etc.)
2. topics_touched: Lista de categorías legales o comerciales afectadas (ej: "Plazo", "Pago", "Responsabilidad", "Confidencialidad", etc.)
3. summary_of_the_change: Resumen COMPRENSIVO que capture la esencia de TODOS los cambios de forma coherente y ejecutiva, explicando:
   - Qué se modificó (cambios principales)
   - Cómo se modificó (especificidades)
   - Por qué se modificó (contexto o razón)
   - El impacto general de los cambios

El resumen debe ser texto narrativo claro, no JSON.
4. El JSON debe ser válido y parseable
5. No incluyas comentarios fuera del JSON"""
        
        # Span principal: Extracción de cambios
        trace_context = {"trace_id": trace_id} if trace_id else None
        with self.langfuse_client.start_as_current_observation(
            trace_context=trace_context,
            name="change-extractor-extract-changes",
            as_type="span",
            input={"text_1_length": len(text_1), "text_2_length": len(text_2)},
            metadata={"type": "agent_operation", "agent": "ChangeExtractorAgent"}
        ) as extractor_span:
            # Llamar a OpenAI para extraer cambios (autotraced por langfuse.openai)
            response = openai.chat.completions.create(
                name="extract-changes",
                trace_id=trace_id,
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en análisis de cambios en documentos. Tu tarea es identificar, aislar y clasificar cada cambio entre dos versiones de un documento. Debes ser exhaustivo y preciso."
                    },
                    {
                        "role": "user",
                        "content": custom_prompt
                    }
                ]
            )
            
            changes_text = response.choices[0].message.content
            
            # Span: Parsing de JSON
            with self.langfuse_client.start_as_current_observation(
                trace_context=trace_context,
                name="parse-json-response",
                as_type="span",
                input={"raw_response_length": len(changes_text)},
                metadata={"type": "json_processing"}
            ) as parse_span:
                try:
                    # Intentar extraer JSON si está envuelto en markdown
                    if "```json" in changes_text:
                        start = changes_text.find("```json") + 7
                        end = changes_text.find("```", start)
                        changes_text = changes_text[start:end].strip()
                    elif "```" in changes_text:
                        start = changes_text.find("```") + 3
                        end = changes_text.find("```", start)
                        changes_text = changes_text[start:end].strip()
                    
                    changes_dict = json.loads(changes_text)
                    parse_span.update(output={"parsed_keys": list(changes_dict.keys())})
                except json.JSONDecodeError as e:
                    parse_span.update(output={"status": "error", "error": str(e)})
                    extractor_span.update(output={"status": "error", "error": str(e)})
                    return {
                        "status": "error",
                        "error": "No se pudo parsear la respuesta como JSON válido",
                        "raw_response": changes_text
                    }
            
            # Span: Validación Pydantic
            with self.langfuse_client.start_as_current_observation(
                trace_context=trace_context,
                name="validate-pydantic-model",
                as_type="span",
                input={"model": "ContractChangeOutput", "fields": list(changes_dict.keys())},
                metadata={"type": "validation"}
            ) as validation_span:
                try:
                    validated_changes = ContractChangeOutput(**changes_dict)
                    validation_span.update(output={"status": "success", "validated": True})
                    extractor_span.update(output={"status": "success", "changes_count": len(changes_dict)})
                    return {
                        "status": "success",
                        "changes": validated_changes.model_dump(),
                        "validated": True
                    }
                except Exception as e:
                    validation_span.update(output={"status": "validation_error", "error": str(e)})
                    extractor_span.update(output={"status": "validation_error", "error": str(e)})
                    return {
                        "status": "validation_error",
                        "error": str(e),
                        "changes": changes_dict,
                        "validated": False
                    }


class ContextualizationAgent:
    """Agente especializado en analizar y mapear la estructura contextual de documentos."""
    
    def __init__(self, langfuse_client: Optional[Langfuse] = None):
        self.langfuse_client = langfuse_client or Langfuse()
    
    def build_context_map(self, analysis_1: str, analysis_2: str, custom_prompt: Optional[str] = None, trace_id: Optional[str] = None) -> dict:
        """
        Analiza la estructura comparada de dos documentos y construye un mapa contextual.
        
        Args:
            analysis_1: Análisis parseado del primer documento
            analysis_2: Análisis parseado del segundo documento
            custom_prompt: Prompt personalizado (opcional)
            trace_id: ID del trace de Langfuse (opcional)
        
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
        
        # Span principal: Construcción del mapa contextual
        trace_context = {"trace_id": trace_id} if trace_id else None
        with self.langfuse_client.start_as_current_observation(
            trace_context=trace_context,
            name="contextualization-build-context-map",
            as_type="span",
            input={"analysis_1_length": len(analysis_1), "analysis_2_length": len(analysis_2)},
            metadata={"type": "agent_operation", "agent": "ContextualizationAgent"}
        ) as context_span:
            # Llamar a OpenAI para el análisis contextual (autotraced por langfuse.openai)
            response = openai.chat.completions.create(
                name="build-context-map",
                trace_id=trace_id,
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
            context_span.update(output={"context_map_length": len(context_map)})
        
            return {
                "status": "success",
                "context_map": context_map
            }



class ImageComparisonWorkflow:
    """Orquesta el flujo de comparación de imágenes con cuatro agentes."""
    
    def __init__(self, langfuse_client: Optional[Langfuse] = None):
        self.langfuse_client = langfuse_client or Langfuse()
        self.reader_agent = ImageReaderAgent(self.langfuse_client)
        self.contextualization_agent = ContextualizationAgent(self.langfuse_client)
        self.text_extractor_agent = TextExtractorAgent(self.langfuse_client)
        self.change_extractor_agent = ChangeExtractorAgent(self.langfuse_client)
    
    def process(
        self,
        image_path_1: str,
        image_path_2: str,
        reader_prompt: Optional[str] = None,
        contextualization_prompt: Optional[str] = None,
        text_extractor_prompt: Optional[str] = None,
        change_extractor_prompt: Optional[str] = None
    ) -> dict:
        """
        Ejecuta el flujo completo de análisis con cuatro agentes:
        1. Agente Lector: Analiza la estructura de ambos documentos
        2. Agente Contextualizador: Mapea la estructura comparada
        3. Agente Extractor de Texto: Extrae el texto completo de forma fiel
        4. Agente Extractor de Cambios: Identifica y clasifica cambios
        
        Args:
            image_path_1: Ruta a la primera imagen
            image_path_2: Ruta a la segunda imagen
            reader_prompt: Prompt personalizado para el agente lector (opcional)
            contextualization_prompt: Prompt personalizado para contextualizador (opcional)
            text_extractor_prompt: Prompt personalizado para extractor de texto (opcional)
            change_extractor_prompt: Prompt personalizado para extractor de cambios (opcional)
        
        Returns:
            Diccionario con los resultados de todos los agentes
        """
        # Crear un trace ID para toda la sesión
        trace_id = self.langfuse_client.create_trace_id()
        trace_context = {"trace_id": trace_id}
        
        # Span principal: Workflow completo
        with self.langfuse_client.start_as_current_observation(
            trace_context=trace_context,
            name="image-comparison-workflow",
            as_type="span",
            input={"image_path_1": image_path_1, "image_path_2": image_path_2},
            metadata={"type": "workflow", "version": "4-agents"}
        ) as workflow_span:
        
            # Paso 1: Agente Lector - Analizar ambas imágenes
            analysis_result = self.reader_agent.analyze(
                image_path_1,
                image_path_2,
                reader_prompt,
                trace_id
            )
            
            if analysis_result["status"] != "success":
                workflow_span.update(output={"status": "error", "failed_at": "reader_agent"})
                return {"error": "Reader agent failed"}
            
            # Extraer análisis individuales para pasar al siguiente agente
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
                contextualization_prompt,
                trace_id
            )
            
            if contextualization_result["status"] != "success":
                workflow_span.update(output={"status": "error", "failed_at": "contextualization_agent"})
                return {"error": "Contextualization agent failed"}
            
            # Paso 3: Agente Extractor de Texto - Extraer texto completo de contratos
            text_extraction_result = self.text_extractor_agent.extract_text(
                image_path_1,
                image_path_2,
                text_extractor_prompt,
                trace_id
            )
            
            if text_extraction_result["status"] != "success":
                workflow_span.update(output={"status": "error", "failed_at": "text_extractor_agent"})
                return {"error": "Text extractor agent failed"}
            
            # Paso 4: Agente Extractor de Cambios - Identificar y clasificar cambios
            change_extraction_result = self.change_extractor_agent.extract_changes(
                text_extraction_result["text_1"],
                text_extraction_result["text_2"],
                contextualization_result["context_map"],
                change_extractor_prompt,
                trace_id
            )
            
            if change_extraction_result["status"] not in ["success", "validation_error"]:
                workflow_span.update(output={"status": "error", "failed_at": "change_extractor_agent"})
                return {"error": "Change extractor agent failed"}
            
            workflow_span.update(output={"status": "success", "agents_executed": 4})
        
        return {
            "status": "success",
            "trace_id": trace_id,
            "image_analysis": analysis_result,
            "context_map": contextualization_result,
            "extracted_text": text_extraction_result,
            "extracted_changes": change_extraction_result
        }

