# Datos de prueba — PIM4 LegalMove

Este directorio contiene **2 pares de contratos** (4 imágenes PNG) para probar el pipeline.

## Estructura

```
test_contracts/
├── pair1_simple/              # Par 1: cambios simples
│   ├── contrato_original.png   # Contrato de servicios (4 cláusulas)
│   ├── adenda_simple.png       # Adenda que modifica 1 cláusula (duración)
│   └── expected.json           # Golden case: resultado esperado
├── pair2_complex/              # Par 2: cambios complejos
│   ├── contrato_original.png   # Contrato de confidencialidad (3 cláusulas)
│   ├── adenda_compleja.png     # Adenda con 3 tipos de cambio
│   └── expected.json           # Golden case: resultado esperado
├── generate_data.py            # Script que regenera las imágenes
└── README.md                   # Este archivo
```

## Par 1 — Cambios simples

**Contrato:** Comercial de servicios (4 cláusulas: pago, duración, territorio, confidencialidad).

**Adenda:** Modifica únicamente la cláusula 2 (duración: 12 → 18 meses).

| Tipo de cambio | Cláusula | Detalle |
|---|---|---|
| Modificación | 2 | Duración: 12 → 18 meses |

**Resultado esperado:**
```json
{
  "sections_changed": ["duration"],
  "topics_touched": ["duracion contractual"],
  "summary_of_the_change": "La duracion del contrato se extiende de 12 a 18 meses."
}
```

## Par 2 — Cambios complejos

**Contrato:** Confidencialidad (3 cláusulas: territorio, restricción de uso, duración).

**Adenda:** 3 tipos de cambio distintos (adición, eliminación, modificación).

| Tipo de cambio | Cláusula | Detalle |
|---|---|---|
| Modificación | 1 | Alcance: Argentina → Argentina + Uruguay + Paraguay |
| Eliminación | 2 | Se remueve la restricción de uso |
| Adición | 4 (nueva) | Difusión controlada a subcontratistas |

**Resultado esperado:**
```json
{
  "sections_changed": ["service_territory", "use_restriction", "controlled_disclosure"],
  "topics_touched": ["alcance territorial", "restriccion de uso", "difusion controlada a terceros"],
  "summary_of_the_change": "Modificacion: el alcance territorial se amplia..."
}
```

## Casos degradados — para poner a prueba Vision

Además de los 2 pares limpios, hay **4 pares degradados** que simulan documentos del
mundo real (manchados, borrosos, rotos) para estresar el parser multimodal (GPT-4o Vision):

| Carpeta | Contrato | Degradación | Cambio esperado |
|---|---|---|---|
| `pair3_alquiler_cafe/` | Locación | ☕ Manchas de café | Canon $50.000 → $65.000 |
| `pair4_laboral_borroso/` | Laboral | 🌫️ Borroso + ruido | Jornada 40→30 hs y sueldo $300k→$260k |
| `pair5_compraventa_roto/` | Compraventa | 📄 Papel roto/rasgado + desvaído | Entrega 30→45 días + financiación (adición) |
| `pair6_extremo/` | Mantenimiento | 💥 Café + blur + ruido + rotación | Respuesta 48→24 hs y precio $80k→$95k |

Cada carpeta trae `contrato_original.png`, `adenda.png` y `expected.json` (orientativo).

**Qué se aprende con estos casos:**
- Vision suele leer bien documentos manchados o levemente borrosos (ej. `pair3` con café).
- En el borde de legibilidad (`pair6` extremo), el resultado puede ser **impreciso** o el
  modelo puede no extraer cambios. En ese caso la **validación Pydantic** frena el output
  vacío y `main.py` muestra un error claro (no inventa un resultado).

Ejecutar un caso degradado:

```bash
python src/main.py data/test_contracts/pair3_alquiler_cafe/contrato_original.png data/test_contracts/pair3_alquiler_cafe/adenda.png
```

## Regenerar las imágenes

```bash
# Pares limpios (pair1, pair2)
python data/test_contracts/generate_data.py

# Pares degradados (pair3–pair6)
python data/test_contracts/generate_stress_cases.py
```

Las imágenes se generan con Pillow (PIL) dibujando texto sobre un lienzo blanco y
aplicando efectos (café, desenfoque, ruido, rasgado, rotación) para simular escaneos reales.
