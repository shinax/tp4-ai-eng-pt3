"""Genera contratos DEGRADADOS para poner a prueba GPT-4o Vision.

Reutiliza el dibujo de documentos de generate_data.py y aplica efectos realistas:
café derramado, escaneo borroso, papel roto/rasgado y un caso extremo combinado.

Pares generados:
    pair3_alquiler_cafe/     -> contrato de locación + adenda   (MANCHAS DE CAFÉ)
    pair4_laboral_borroso/   -> contrato laboral + adenda        (BORROSO)
    pair5_compraventa_roto/  -> contrato compraventa + adenda    (ROTO / RASGADO)
    pair6_extremo/           -> contrato de servicios + adenda   (CAFÉ + BLUR + RUIDO + ROTACIÓN)

Cada carpeta trae: contrato_original.png, adenda.png y expected.json (orientativo).

Uso:
    python data/test_contracts/generate_stress_cases.py
"""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

# Reutilizamos el dibujo base y el guardado de golden del generador principal.
from generate_data import draw_doc, save_expected

OUTPUT_DIR = Path(__file__).parent


# ============================================================================
#  Efectos de degradación (para estresar el parser de Vision)
# ============================================================================


def add_coffee_stain(img: Image.Image, seed: int = 0) -> Image.Image:
    """Superpone manchas de café translúcidas con anillo de taza y goteos."""
    random.seed(seed)
    base = img.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    w, h = base.size
    for _ in range(random.randint(2, 3)):
        cx = random.randint(int(w * 0.25), int(w * 0.80))
        cy = random.randint(int(h * 0.20), int(h * 0.80))
        r = random.randint(55, 110)
        od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(115, 74, 22, 55))  # relleno
        od.ellipse(
            [cx - r, cy - r, cx + r, cy + r], outline=(90, 55, 15, 130), width=7
        )  # borde de taza
        for _ in range(random.randint(4, 7)):  # goteos
            gx = cx + random.randint(-r, r)
            gy = cy + random.randint(-r, r)
            gr = random.randint(4, 13)
            od.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(100, 60, 18, 65))
    return Image.alpha_composite(base, overlay).convert("RGB")


def add_blur(img: Image.Image, radius: float = 1.5) -> Image.Image:
    """Simula un escaneo desenfocado."""
    return img.filter(ImageFilter.GaussianBlur(radius))


def add_noise(img: Image.Image, amount: float = 0.05, seed: int = 0) -> Image.Image:
    """Agrega ruido tipo fotocopia/escaneo viejo (píxeles oscuros dispersos)."""
    random.seed(seed)
    px = img.load()
    w, h = img.size
    for _ in range(int(w * h * amount)):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        v = random.randint(0, 70)
        px[x, y] = (v, v, v)
    return img


def add_torn(img: Image.Image, seed: int = 0) -> Image.Image:
    """Simula papel rasgado en el borde derecho (parte del texto se pierde)."""
    random.seed(seed)
    base = img.copy()
    d = ImageDraw.Draw(base)
    w, h = base.size
    puntos = [(w, 0)]
    for y in range(0, h, 18):
        x = w - random.randint(0, 70)
        puntos.append((x, y))
    puntos.append((w, h))
    d.polygon(puntos, fill=(255, 255, 255))  # zona rasgada (papel faltante)
    d.line(puntos[1:-1], fill=(170, 170, 170), width=2)  # sombra del borde
    return base


def add_faded(img: Image.Image, factor: float = 0.55) -> Image.Image:
    """Desvanece el documento mezclándolo con blanco (tinta gastada)."""
    white = Image.new("RGB", img.size, (255, 255, 255))
    return Image.blend(img, white, 1 - factor)


def add_rotation(img: Image.Image, angle: float = 3.0) -> Image.Image:
    """Inclina levemente el documento (como escaneo torcido)."""
    return img.rotate(angle, expand=True, fillcolor=(255, 255, 255))


# ============================================================================
#  Par 3 — Contrato de LOCACIÓN (manchas de café)
# ============================================================================


def contrato_alquiler() -> Image.Image:
    return draw_doc(
        "CONTRATO DE LOCACION",
        "Version original - Marzo 2024",
        [
            (
                "1",
                "Canon mensual",
                "El locatario abonara un canon mensual de pesos cincuenta mil ($50.000), "
                "pagadero del 1 al 10 de cada mes.",
            ),
            (
                "2",
                "Duracion de la locacion",
                "La locacion tendra una duracion de veinticuatro (24) meses contados desde la firma.",
            ),
            (
                "3",
                "Deposito en garantia",
                "El locatario entrega en concepto de deposito una suma equivalente a dos (2) "
                "meses de canon locativo.",
            ),
        ],
        color=(252, 250, 244),
    )


def adenda_alquiler() -> Image.Image:
    return draw_doc(
        "ADENDA - CONTRATO DE LOCACION",
        "Modificacion - Septiembre 2024",
        [
            (
                "1 modificada",
                "Nuevo canon mensual",
                "Por acuerdo de partes, el canon mensual se incrementa a pesos sesenta y cinco "
                "mil ($65.000) a partir del septimo mes de vigencia, quedando sin efecto el "
                "monto anterior de $50.000.",
            ),
        ],
        color=(255, 255, 247),
        height=560,
    )


# ============================================================================
#  Par 4 — Contrato LABORAL (borroso)
# ============================================================================


def contrato_laboral() -> Image.Image:
    return draw_doc(
        "CONTRATO DE TRABAJO",
        "Version original - Enero 2024",
        [
            (
                "1",
                "Jornada laboral",
                "El trabajador cumplira una jornada de cuarenta (40) horas semanales, "
                "distribuidas de lunes a viernes.",
            ),
            (
                "2",
                "Remuneracion",
                "El empleador abonara una remuneracion mensual de pesos trescientos mil ($300.000).",
            ),
            (
                "3",
                "Vacaciones",
                "El trabajador gozara de catorce (14) dias corridos de vacaciones anuales.",
            ),
        ],
        color=(248, 250, 252),
    )


def adenda_laboral() -> Image.Image:
    return draw_doc(
        "ADENDA - CONTRATO DE TRABAJO",
        "Modificacion - Junio 2024",
        [
            (
                "1 modificada",
                "Nueva jornada laboral",
                "La jornada semanal se reduce de cuarenta (40) a treinta (30) horas semanales.",
            ),
            (
                "2 modificada",
                "Nueva remuneracion",
                "En consecuencia, la remuneracion mensual se ajusta de $300.000 a pesos "
                "doscientos sesenta mil ($260.000).",
            ),
        ],
        color=(255, 255, 247),
        height=620,
    )


# ============================================================================
#  Par 5 — Contrato de COMPRAVENTA (roto / rasgado)
# ============================================================================


def contrato_compraventa() -> Image.Image:
    return draw_doc(
        "CONTRATO DE COMPRAVENTA",
        "Version original - Febrero 2024",
        [
            (
                "1",
                "Precio",
                "El comprador abonara por el bien la suma de pesos un millon doscientos mil ($1.200.000).",
            ),
            (
                "2",
                "Plazo de entrega",
                "El vendedor entregara el bien dentro de los treinta (30) dias corridos desde la firma.",
            ),
            (
                "3",
                "Garantia",
                "El bien cuenta con una garantia de doce (12) meses por defectos de fabricacion.",
            ),
        ],
        color=(250, 250, 248),
    )


def adenda_compraventa() -> Image.Image:
    return draw_doc(
        "ADENDA - CONTRATO DE COMPRAVENTA",
        "Modificacion - Mayo 2024",
        [
            (
                "2 modificada",
                "Nuevo plazo de entrega",
                "El plazo de entrega se extiende de treinta (30) a cuarenta y cinco (45) dias corridos.",
            ),
            (
                "4 agregada",
                "Financiacion",
                "Se incorpora la posibilidad de abonar el precio en tres (3) cuotas mensuales "
                "sin interes.",
            ),
        ],
        color=(255, 255, 247),
        height=620,
    )


# ============================================================================
#  Par 6 — Contrato de SERVICIOS (extremo: café + blur + ruido + rotacion)
# ============================================================================


def contrato_servicios_mant() -> Image.Image:
    return draw_doc(
        "CONTRATO DE MANTENIMIENTO",
        "Version original - Abril 2024",
        [
            (
                "1",
                "Alcance del servicio",
                "El proveedor realizara mantenimiento preventivo mensual de los equipos del cliente.",
            ),
            (
                "2",
                "Precio del servicio",
                "El servicio tendra un costo de pesos ochenta mil ($80.000) mensuales.",
            ),
            (
                "3",
                "Tiempo de respuesta",
                "Ante fallas, el proveedor respondera en un plazo maximo de cuarenta y ocho (48) horas.",
            ),
        ],
        color=(250, 248, 245),
    )


def adenda_servicios_mant() -> Image.Image:
    return draw_doc(
        "ADENDA - CONTRATO DE MANTENIMIENTO",
        "Modificacion - Octubre 2024",
        [
            (
                "3 modificada",
                "Nuevo tiempo de respuesta",
                "El tiempo de respuesta ante fallas se reduce de cuarenta y ocho (48) a "
                "veinticuatro (24) horas.",
            ),
            (
                "2 modificada",
                "Nuevo precio",
                "El costo mensual del servicio asciende de $80.000 a pesos noventa y cinco mil ($95.000).",
            ),
        ],
        color=(255, 255, 247),
        height=620,
    )


# ============================================================================
#  Orquestación: aplica degradaciones, guarda PNGs y golden
# ============================================================================


def _save(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG", dpi=(150, 150))
    print(f"  OK {path.parent.name}/{path.name}")


def main() -> None:
    print("Generando contratos DEGRADADOS para estresar Vision...\n")

    # --- Par 3: café ---
    print("Par 3 (locacion + CAFÉ):")
    d3 = OUTPUT_DIR / "pair3_alquiler_cafe"
    _save(add_coffee_stain(contrato_alquiler(), seed=3), d3 / "contrato_original.png")
    _save(add_coffee_stain(adenda_alquiler(), seed=33), d3 / "adenda.png")
    save_expected(
        d3 / "expected.json",
        {
            "sections_changed": ["canon_mensual"],
            "topics_touched": ["canon mensual de locacion"],
            "summary_of_the_change": "El canon mensual se incrementa de $50.000 a $65.000 a partir del septimo mes.",
        },
    )

    # --- Par 4: borroso ---
    print("\nPar 4 (laboral + BORROSO):")
    d4 = OUTPUT_DIR / "pair4_laboral_borroso"
    _save(
        add_noise(add_blur(contrato_laboral(), 1.6), 0.03, seed=4),
        d4 / "contrato_original.png",
    )
    _save(add_noise(add_blur(adenda_laboral(), 1.6), 0.03, seed=44), d4 / "adenda.png")
    save_expected(
        d4 / "expected.json",
        {
            "sections_changed": ["jornada_laboral", "remuneracion"],
            "topics_touched": ["jornada laboral", "remuneracion mensual"],
            "summary_of_the_change": "La jornada se reduce de 40 a 30 horas semanales y la remuneracion se ajusta de $300.000 a $260.000.",
        },
    )

    # --- Par 5: roto ---
    print("\nPar 5 (compraventa + ROTO):")
    d5 = OUTPUT_DIR / "pair5_compraventa_roto"
    _save(
        add_faded(add_torn(contrato_compraventa(), seed=5), 0.7),
        d5 / "contrato_original.png",
    )
    _save(add_faded(add_torn(adenda_compraventa(), seed=55), 0.7), d5 / "adenda.png")
    save_expected(
        d5 / "expected.json",
        {
            "sections_changed": ["plazo_entrega", "financiacion"],
            "topics_touched": ["plazo de entrega", "financiacion en cuotas"],
            "summary_of_the_change": "El plazo de entrega se extiende de 30 a 45 dias y se agrega una clausula de financiacion en 3 cuotas sin interes.",
        },
    )

    # --- Par 6: extremo (todo junto) ---
    print("\nPar 6 (mantenimiento + EXTREMO: café + blur + ruido + rotacion):")
    d6 = OUTPUT_DIR / "pair6_extremo"
    orig6 = add_rotation(
        add_noise(
            add_blur(add_coffee_stain(contrato_servicios_mant(), 6), 1.3), 0.04, 6
        ),
        2.5,
    )
    aden6 = add_rotation(
        add_noise(
            add_blur(add_coffee_stain(adenda_servicios_mant(), 66), 1.3), 0.04, 66
        ),
        -2.5,
    )
    _save(orig6, d6 / "contrato_original.png")
    _save(aden6, d6 / "adenda.png")
    save_expected(
        d6 / "expected.json",
        {
            "sections_changed": ["precio", "tiempo_respuesta"],
            "topics_touched": ["precio del servicio", "tiempo de respuesta"],
            "summary_of_the_change": "El tiempo de respuesta se reduce de 48 a 24 horas y el precio sube de $80.000 a $95.000.",
        },
    )

    print(f"\nContratos degradados generados en: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
