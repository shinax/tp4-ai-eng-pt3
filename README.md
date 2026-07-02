# 🤖 Sistema de Análisis de Contratos con Agentes IA

Una aplicación Python de **cuatro agentes de IA** que leen, contextualizan, extraen y comparan contratos usando OpenAI Vision (GPT-4o), con trazas completas en Langfuse y validación estructurada con Pydantic.

## ✨ Características Principales

- **🤖 Cuatro Agentes Especializados** en pipeline secuencial:
  - **Agente 1 (Lector)**: Analiza la estructura de ambos documentos
  - **Agente 2 (Contextualizador)**: Mapea estructura comparada e identifica correspondencias
  - **Agente 3 (Extractor de Texto)**: Extrae el texto completo preservando estructura
  - **Agente 4 (Extractor de Cambios)**: Identifica, aísla y clasifica cambios con validación Pydantic
  
- **📊 Trazas Completas en Langfuse**: Monitoreo automático de cada llamada a GPT-4o
- **✅ Validación Estructurada**: Modelos Pydantic para garantizar calidad de datos
- **🖼️ Soporte Multi-formato**: JPG, PNG, GIF, WebP
- **⚙️ Configuración Flexible**: Prompts personalizables por agente
- **📦 Modular y Extensible**: Arquitectura lista para agregar más agentes (Reportes, Análisis Adicional, etc.)
- **🗺️ Análisis Comparativo Sofisticado**: Cambios clasificados en adiciones, eliminaciones y modificaciones

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Clonar el proyecto
cd /Users/jennifer.hughes/Documents/henry4/tp4-ai-eng-pt3

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración

Asegúrate de que el archivo `.env` contenga:

```env
OPENAI_API_KEY=sk-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
```

### 3. Ejecución

```bash
# Opción 1: Prueba rápida con imágenes de prueba
python test_app.py

# Opción 2: Con contratos reales
python example.py --image1 ./examples/documento_1__original.jpg --image2 ./examples/documento_1__enmienda.jpg

# Opción 3: Con prompts personalizados
python example.py --image1 doc1.jpg --image2 doc2.jpg --reader-prompt "Enfócate en cláusulas legales"
```

## 📚 Estructura del Proyecto

```
├── main.py                    # Aplicación principal
├── agents.py                  # Clases de agentes
├── config.py                  # Configuración centralizada
├── utils.py                   # Utilidades y formateadores
├── example.py                 # Script CLI de ejemplos
├── test_app.py                # Script de pruebas
├── requirements.txt           # Dependencias
├── USAGE.md                   # Documentación detallada
└── .env                       # Variables de entorno
```

## 🏗️ Arquitectura de Agentes (4 Agentes)

```
┌──────────────────────────────────────────────┐
│     IMAGEN 1       │       IMAGEN 2          │
└────────┬──────────────────────┬──────────────┘
         │                      │
    ┌────▼──────────────────────▼──────────────┐
    │   AGENTE 1: ImageReaderAgent             │
    │   ▪ Lee ambas imágenes                   │
    │   ▪ Analiza estructura visual            │
    │   ▪ Extrae características               │
    │   ▪ Genera análisis detallado            │
    └────┬─────────────────────────────────────┘
         │
    ┌────▼─────────────────────────────────────┐
    │ AGENTE 2: ContextualizationAgent         │
    │ ▪ Mapea estructura comparada             │
    │ ▪ Identifica secciones equivalentes      │
    │ ▪ Establece correspondencias             │
    │ ▪ Analiza cambios estructurales          │
    │ ▪ Propone mapa de relaciones             │
    └────┬─────────────────────────────────────┘
         │
    ┌────▼─────────────────────────────────────┐
    │ AGENTE 3: TextExtractorAgent             │
    │ ▪ Extrae texto completo de imágenes      │
    │ ▪ Mantiene estructura original           │
    │ ▪ Preserva formato y puntuación          │
    │ ▪ Marca secciones ilegibles              │
    │ ▪ Prepara texto para análisis            │
    └────┬─────────────────────────────────────┘
         │
    ┌────▼─────────────────────────────────────┐
    │ AGENTE 4: ChangeExtractorAgent           │
    │ ▪ Identifica cambios específicos         │
    │ ▪ Clasifica en adiciones/eliminaciones   │
    │ ▪ Detecta modificaciones                 │
    │ ▪ Describe razones de cambios            │
    │ ▪ Valida con modelos Pydantic            │
    │ ▪ Retorna JSON estructurado              │
    └────┬─────────────────────────────────────┘
         │
    ┌────▼─────────────────────────────────────┐
    │   SALIDA FINAL                           │
    │ ▪ Análisis de estructura                 │
    │ ▪ Mapa contextual                        │
    │ ▪ Texto extraído (ambos documentos)      │
    │ ▪ Cambios clasificados                   │
    │ ▪ Listo para reportes/acción             │
    └──────────────────────────────────────────┘
```

## 💻 Ejemplos de Uso

### Uso Básico con CLI

```bash
python example.py --image1 screenshot_before.png --image2 screenshot_after.png
```

### Con Prompts Personalizados

```bash
python example.py \
  --image1 doc1.jpg \
  --image2 doc2.jpg \
  --reader-prompt "Identifica el tipo de documento y estructura" \
  --text-extractor-prompt "Extrae solo las secciones principales"
```

### Desde Código Python

```python
from dotenv import load_dotenv
from langfuse import Langfuse
from agents import ImageComparisonWorkflow

load_dotenv()

# Inicializar
langfuse_client = Langfuse()
workflow = ImageComparisonWorkflow(langfuse_client)

# Procesar
result = workflow.process("image1.jpg", "image2.jpg")

# Mostrar resultados
print("Análisis:", result["image_analysis"]["analysis"])
print("Contexto:", result["context_map"]["context_map"])
print("Texto 1:", result["extracted_text"]["text_1"])
print("Texto 2:", result["extracted_text"]["text_2"])

#  Acceder a cambios clasificados
changes = result["extracted_changes"]["changes"]
print(f"\nAdiciones detectadas: {len(changes.additions)}")
for addition in changes.additions:
    print(f"  - {addition.section}: {addition.description}")

print(f"\nModificaciones detectadas: {len(changes.modifications)}")
for mod in changes.modifications:
    print(f"  - {mod.section}: {mod.description}")

# Flush para asegurar que las trazas se envíen
langfuse_client.flush()
```

## 📊 Monitoreo en Langfuse

Después de ejecutar, accede a tu dashboard en https://cloud.langfuse.com para ver:

- **Timeline**: Duración de cada generación de IA
- **Inputs/Outputs**: Prompts y respuestas completamente
- **Metadata**: Información contextual (rutas de imágenes, etc.)
- **Tokens**: Consumo de tokens por llamada
- **Errores**: Stack traces si algo falla

## 🔧 API de Agentes

### ImageReaderAgent

```python
from agents import ImageReaderAgent
from langfuse import Langfuse

agent = ImageReaderAgent(Langfuse())

result = agent.analyze(
    "image1.jpg",
    "image2.jpg",
    custom_prompt="Tu prompt aquí"
)

print(result["analysis"])
```

### ContextualizationAgent

```python
from agents import ContextualizationAgent
from langfuse import Langfuse

agent = ContextualizationAgent(Langfuse())

# Usando análisis previos del ImageReaderAgent
result = agent.build_context_map(
    analysis_1,  # Análisis de imagen 1
    analysis_2,  # Análisis de imagen 2
    custom_prompt="Tu prompt personalizado"
)

print(result["context_map"])
```

### TextExtractorAgent

```python
from agents import TextExtractorAgent
from langfuse import Langfuse

agent = TextExtractorAgent(Langfuse())

result = agent.extract_text(
    "image1.jpg",
    "image2.jpg",
    custom_prompt="Tu prompt personalizado"
)

print(result["text_1"])  # Texto del contrato 1
print(result["text_2"])  # Texto del contrato 2
```

### ChangeExtractorAgent 

```python
from agents import ChangeExtractorAgent
from langfuse import Langfuse

agent = ChangeExtractorAgent(Langfuse())

# Usando textos del TextExtractorAgent y mapa del ContextualizationAgent
result = agent.extract_changes(
    text_1="Texto del documento 1...",
    text_2="Texto del documento 2...",
    context_map=context_map_from_contextualization,
    custom_prompt="Tu prompt personalizado"
)

# Acceder a cambios validados con Pydantic
if result["status"] == "success":
    changes = result["changes"]
    print(f"Adiciones: {len(changes.additions)}")
    print(f"Eliminaciones: {len(changes.deletions)}")
    print(f"Modificaciones: {len(changes.modifications)}")
    
    for mod in changes.modifications:
        print(f"  - {mod.section}: {mod.description}")
```

### ImageComparisonWorkflow

```python
from agents import ImageComparisonWorkflow
from langfuse import Langfuse

workflow = ImageComparisonWorkflow(Langfuse())

result = workflow.process(
    "image1.jpg",
    "image2.jpg",
    reader_prompt="Prompt para agente 1 (opcional)",
    contextualization_prompt="Prompt para agente 2 (opcional)",
    text_extractor_prompt="Prompt para agente 3 (opcional)",
    change_extractor_prompt="Prompt para agente 4 (opcional)"
)

# Acceder a resultados de todos los agentes
print(result["image_analysis"])       # Agente 1: Análisis de estructura
print(result["context_map"])          # Agente 2: Mapa contextual
print(result["extracted_text"])       # Agente 3: Texto extraído
print(result["extracted_changes"])    # Agente 4: Cambios clasificados
```

## 🎯 Mejores Prácticas Implementadas

### ✅ Modularización
- Cada agente es una clase independiente
- Fácil de reutilizar y extender
- Responsabilidades bien definidas

### ✅ Trazas Completas
- Cada operación genera una traza en Langfuse
- Seguimiento completo del flujo
- Observabilidad de todas las llamadas a GPT-4o

### ✅ Validación Estructurada
- Modelos Pydantic para garantizar calidad
- Validación de salidas de IA
- Manejo de errores de validación

### ✅ Manejo Robusto de Errores
- Validación de imágenes
- Checks de status
- Mensajes descriptivos y accionables

### ✅ Configuración Flexible
- Variables de entorno centralizadas
- Prompts personalizables por agente
- Fácil de adaptar a nuevos casos de uso

### ✅ Codificación Segura
- Base64 para transmisión de imágenes
- Detección automática de MIME types
- Soporte multi-formato (JPG, PNG, GIF, WebP)

## 🔐 Variables de Entorno

```env
# OpenAI API
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# Langfuse Tracing
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com

# Logging
LOG_LEVEL=INFO
ENABLE_TRACE_LOGGING=true

# Timeouts (segundos)
OPENAI_TIMEOUT=60
IMAGE_READ_TIMEOUT=30
