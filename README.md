# 🤖 Sistema de Comparación de Imágenes con Agentes IA

Una aplicación Python de dos agentes de IA que lee y compara imágenes usando OpenAI Vision, con trazas completas en Langfuse.

## ✨ Características Principales

- **🤖 Dos Agentes Especializados**:
  - **Agente 1 (Lector)**: Lee y analiza dos imágenes en detalle
  - **Agente 2 (Comparador)**: Compara los análisis y encuentra diferencias
  
- **📊 Trazas Completas en Langfuse**: Monitoreo de cada paso del proceso
- **🖼️ Soporte Multi-formato**: JPG, PNG, GIF, WebP
- **⚙️ Configuración Flexible**: Prompts personalizables por agente
- **📦 Modular y Reutilizable**: Fácil de extender con nuevos agentes

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Clonar el proyecto
cd /Users/jennifer.hughes/Documents/henry4/tp4-ai-eng-pt3

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración

Asegúrate de que el archivo `.env` contiene:

```env
OPENAI_API_KEY=sk-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
```

### 3. Ejecución

```bash
# Opción 1: Prueba rápida con imágenes generadas
python test_app.py

# Opción 2: Con tus propias imágenes
python example.py --image1 path/to/image1.jpg --image2 path/to/image2.jpg
```

## 📚 Estructura del Proyecto

```
├── main.py                    # Aplicación principal
├── agents.py                  # Clases de agentes
├── config.py                  # Configuración centralizada
├── utils.py                   # Utilidades y formateadores
├── example.py                 # Script CLI de ejemplos
├── test_app.py               # Script de pruebas
├── requirements.txt           # Dependencias
├── USAGE.md                  # Documentación detallada
└── .env                      # Variables de entorno
```

## 🏗️ Arquitectura de Agentes

```
┌──────────────────────────────────────────────┐
│         IMAGEN 1  │  IMAGEN 2                │
└────────┬──────────────────────┬──────────────┘
         │                      │
    ┌────▼──────────────────────▼────┐
    │   AGENTE 1: ImageReaderAgent   │
    │   ▪ Lee ambas imágenes         │
    │   ▪ Extrae características    │
    │   ▪ Genera análisis detallado │
    └────┬──────────────────────────┘
         │
    ┌────▼──────────────────────────┐
    │ AGENTE 2: ImageComparatorAgent│
    │ ▪ Recibe análisis             │
    │ ▪ Identifica similitudes      │
    │ ▪ Encuentra diferencias       │
    │ ▪ Genera conclusiones         │
    └────┬──────────────────────────┘
         │
    ┌────▼──────────────────────────┐
    │   REPORTE FINAL               │
    │ ▪ Análisis detallado          │
    │ ▪ Comparación completa        │
    │ ▪ Insights y conclusiones     │
    └───────────────────────────────┘
```

## 💻 Ejemplos de Uso

### Uso Básico con CLI

```bash
python example.py --image1 screenshot_before.png --image2 screenshot_after.png
```

### Con Prompts Personalizados

```bash
python example.py \
  --image1 photo1.jpg \
  --image2 photo2.jpg \
  --reader-prompt "Enfócate en los objetos principales" \
  --comparator-prompt "Identifica cambios de color y tamaño"
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
print("Comparación:", result["image_comparison"]["comparison"])

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

### ImageComparatorAgent

```python
from agents import ImageComparatorAgent
from langfuse import Langfuse

agent = ImageComparatorAgent(Langfuse())

result = agent.compare(
    analysis_data={"analysis": "..."},
    custom_prompt="Tu prompt aquí"
)

print(result["comparison"])
```

### ImageComparisonWorkflow

```python
from agents import ImageComparisonWorkflow
from langfuse import Langfuse

workflow = ImageComparisonWorkflow(Langfuse())

result = workflow.process(
    "image1.jpg",
    "image2.jpg",
    reader_prompt="Prompt para agente 1",
    comparator_prompt="Prompt para agente 2"
)
```

## 🎯 Mejores Prácticas Implementadas

### ✅ Modularización
- Cada agente es una clase independiente
- Fácil de reutilizar y extender

### ✅ Trazas Completas
- Cada operación genera una traza en Langfuse
- Seguimiento completo del flujo

### ✅ Manejo Robusto de Errores
- Validación de imágenes
- Checks de status
- Mensajes descriptivos

### ✅ Configuración Flexible
- Variables de entorno centralizadas
- Prompts personalizables
- Fácil de adaptar

### ✅ Codificación Segura
- Base64 para transmisión de imágenes
- Detección automática de MIME types
- Soporte multi-formato

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
```

## 📈 Casos de Uso

### 1. Comparación de Screenshots
```bash
python example.py --image1 before.png --image2 after.png
```

### 2. Análisis de Documentos
```bash
python example.py --image1 page1.jpg --image2 page2.jpg
```

### 3. Control de Calidad de Productos
```bash
python example.py --image1 product_v1.jpg --image2 product_v2.jpg
```

### 4. Detección de Cambios
```bash
python example.py --image1 map_old.png --image2 map_new.png
```

## 🛠️ Extensiones Futuras

- [ ] Agregar más agentes especializados
- [ ] Implementar caché de análisis
- [ ] API REST con FastAPI
- [ ] Procesamiento asincrónico con Celery
- [ ] Webhooks para notificaciones
- [ ] Soporte para URLs remotas de imágenes
- [ ] Dashboard propio de visualización
- [ ] Exportación a múltiples formatos

## 📝 Documentación

Para más información, consulta [USAGE.md](USAGE.md) para una guía detallada y ejemplos avanzados.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver archivo `LICENSE` para más detalles.

## 📞 Soporte

- **Langfuse Docs**: https://docs.langfuse.com
- **OpenAI Vision**: https://platform.openai.com/docs/guides/vision
- **LangChain**: https://python.langchain.com

---

**Creado con ❤️ usando Langfuse + OpenAI + Python**
