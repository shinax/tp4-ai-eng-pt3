
from typing import Optional
from langfuse.openai import openai
from langfuse import Langfuse

from config import OPENAI_MODEL
from models import ContractChangeOutput


class ChangeExtractorAgent:
    """Agente especializado en extraer y clasificar cambios entre dos documentos."""
    
    def __init__(self, langfuse_client: Optional[Langfuse] = None):
        self.langfuse_client = langfuse_client or Langfuse()
    
    def extract_changes(
        self, 
        text_1: str, 
        text_2: str,
        context_map: str,
        custom_prompt: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> ContractChangeOutput:
        """
        Identifica, aísla y describe cada cambio entre dos textos.
        Distingue entre adiciones, eliminaciones y modificaciones.
        
        Args:
            text_1: Texto del documento original
            text_2: Texto del documento con enmienda
            context_map: Mapa contextual del ContextualizationAgent
            custom_prompt: Prompt personalizado (opcional)
            trace_id: ID del trace de Langfuse (opcional)
        
        Returns:
            Diccionario con cambios estructurados y validados
        """
        # Usar prompt personalizado o por defecto
        if custom_prompt is None:
            custom_prompt = """\
            Sos un Auditor Legal con especialización en comparación de contratos \
            y detección de cambios normativos.

            Tu tarea es identificar, aislar y describir cada cambio introducido por \
            la adenda respecto al contrato original, usando el mapa contextual \
            proporcionado por el agente de contextualización.

            Debes distinguir entre:
            - ADICIONES: cláusulas nuevas que no existían en el contrato original.
            - ELIMINACIONES: cláusulas del original que la adenda remueve.
            - MODIFICACIONES: cláusulas que cambian de contenido.

            Completa los campos:
            - sections_changed: palabras cortas que sirvan como identificadores de las secciones modificadas
            (ej: payment_terms, duration, service_territory, use_restriction).
            - topics_touched: temas legales/comerciales afectados (ej: duración contractual).
            - summary_of_the_change: resumen detallado pero conciso, distinguiendo adiciones,
            eliminaciones y modificaciones (mínimo 10 caracteres).
            """
        
        # Llamar a OpenAI para extraer cambios (autotraced por langfuse.openai)
        response = openai.chat.completions.parse(
            name="extract-changes",
            trace_id=trace_id,
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": custom_prompt
                },
                {
                    "role": "user",
                    "content": (
                        "CONTRATO ORIGINAL:\n"
                        f"{text_1}\n\n"
                        "ADENDA:\n"
                        f"{text_2}\n\n"
                        "MAPA CONTEXTUAL:\n"
                        f"{context_map}"
                    )
                }
            ],
            response_format=ContractChangeOutput,
        )
        return response.choices[0].message.parsed


class ContextualizationAgent:
    """Agente especializado en analizar y mapear la estructura contextual de documentos."""
    
    def __init__(self, langfuse_client: Optional[Langfuse] = None):
        self.langfuse_client = langfuse_client or Langfuse()
    
    def build_context_map(self, analysis_1: str, analysis_2: str, custom_prompt: Optional[str] = None, trace_id: Optional[str] = None) -> str:
        """
        Agente 1: Mapea las estructuras analizadas y genera un mapa contextual para cada documento.
        """
        # Usar prompt personalizado o por defecto
        if custom_prompt is None:
            custom_prompt = """\
                Sos un Analista Senior de Contratos con 15 años de experiencia en \
                comparación de documentos legales comerciales.

                Tu tarea es analizar el contrato original y su adenda, y construir \
                un MAPA CONTEXTUAL que servirá de guía para un agente extractor.

                Debes identificar:
                1. Qué secciones o cláusulas existen en cada documento.
                2. Cómo se corresponden entre sí (directas, modificadas, nuevas, eliminadas).
                3. Cuál es el propósito general de cada bloque.

                Reglas estrictas:
                - NO extraigas los cambios finales.
                - NO generes JSON.
                - Devuelve un texto estructurado y claro, organizado por secciones.
                - Si hay ambigüedades o correspondencias parciales, menciónalas.
                """

        # Llamar a OpenAI para el análisis contextual
        response = openai.chat.completions.create(
            name="build-context-map",
            trace_id=trace_id,
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": custom_prompt
                },
                {
                    "role": "user",
                    "content": (
                        "ANALISIS CONTRATO ORIGINAL:\n"
                        f"{analysis_1}\n\n"
                        "ANALISIS ADENDA:\n"
                        f"{analysis_2}"
                    )
                }
            ]
        )
        
        context_map = response.choices[0].message.content
    
        return context_map
