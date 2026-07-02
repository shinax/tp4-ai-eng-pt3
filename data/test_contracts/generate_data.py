"""Genera 4 imagenes PNG (2 pares de contratos) y golden datasets para PIM4.

Pares de prueba:
    Par 1 (simple): Contrato de servicios + adenda que modifica la duracion.
    Par 2 (complejo): Contrato de confidencialidad + adenda que agrega,
        modifica y elimina clausulas.

Output:
    data/test_contracts/pair1_simple/contrato_original.png
    data/test_contracts/pair1_simple/adenda_simple.png
    data/test_contracts/pair1_simple/expected.json
    data/test_contracts/pair2_complex/contrato_original.png
    data/test_contracts/pair2_complex/adenda_compleja.png
    data/test_contracts/pair2_complex/expected.json

Como se usa:
    python data/test_contracts/generate_data.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = Path(__file__).parent
PAIR1_DIR = OUTPUT_DIR / "pair1_simple"
PAIR2_DIR = OUTPUT_DIR / "pair2_complex"
PAIR1_DIR.mkdir(parents=True, exist_ok=True)
PAIR2_DIR.mkdir(parents=True, exist_ok=True)


def get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Busca una fuente TrueType disponible segun el sistema operativo."""
    paths = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def wrap(
    draw: ImageDraw.ImageDraw, text: str, x: int, y: int, font, max_chars: int = 92
) -> int:
    """Envuelve texto en lineas para que quepan en el ancho de la imagen."""
    line = ""
    for word in text.split():
        test = f"{line} {word}".strip()
        if len(test) > max_chars:
            draw.text((x, y), line, fill=(35, 35, 35), font=font)
            y += 22
            line = word
        else:
            line = test
    if line:
        draw.text((x, y), line, fill=(35, 35, 35), font=font)
        y += 22
    return y


def draw_doc(
    title: str,
    subtitle: str,
    clauses: list[tuple[str, str, str]],
    color=(255, 255, 255),
    height=720,
) -> Image.Image:
    """Dibuja un documento legal como imagen PNG con titulo, subtitulos y clausulas."""
    width = 850
    img = Image.new("RGB", (width, height), color=color)
    draw = ImageDraw.Draw(img)
    fonts = {
        "title": get_font(18),
        "sub": get_font(12),
        "head": get_font(13),
        "body": get_font(11),
    }

    draw.rectangle([(0, 0), (width, 86)], fill=(238, 241, 245))
    draw.text((42, 18), title, fill=(15, 35, 80), font=fonts["title"])
    draw.text((42, 52), subtitle, fill=(80, 80, 80), font=fonts["sub"])
    draw.line([(42, 92), (width - 42, 92)], fill=(20, 20, 20), width=2)

    y = 118
    for number, heading, text in clauses:
        draw.text(
            (42, y),
            f"Clausula {number} - {heading}",
            fill=(0, 55, 145),
            font=fonts["head"],
        )
        y += 27
        y = wrap(draw, text, 58, y, fonts["body"])
        y += 18

    y = max(y + 12, height - 118)
    draw.text(
        (42, y), "Firma y sello de las partes:", fill=(80, 80, 80), font=fonts["sub"]
    )
    draw.rectangle([(42, y + 24), (350, y + 76)], outline=(145, 145, 145), width=1)
    draw.rectangle([(455, y + 24), (765, y + 76)], outline=(145, 145, 145), width=1)
    draw.text((42, y + 82), "CLIENTE", fill=(120, 120, 120), font=fonts["sub"])
    draw.text((455, y + 82), "PROVEEDOR", fill=(120, 120, 120), font=fonts["sub"])
    return img


# ============================================================================
# Par 1 — Cambios simples (contrato de servicios)
# La adenda modifica SOLO la duracion (clausula 2).
# ============================================================================


def create_contrato_servicios() -> Image.Image:
    return draw_doc(
        "CONTRATO COMERCIAL DE SERVICIOS",
        "Version original - Enero 2024",
        [
            (
                "1",
                "Monto mensual de pago",
                "El cliente abonara al proveedor la suma de pesos un mil ($1.000) mensuales, "
                "pagaderos dentro de los primeros cinco dias habiles de cada mes.",
            ),
            (
                "2",
                "Duracion del contrato",
                "El presente contrato tendra una vigencia de doce (12) meses, contados a partir "
                "de la fecha de firma del presente instrumento.",
            ),
            (
                "3",
                "Territorio de operacion",
                "El proveedor prestara los servicios objeto de este contrato exclusivamente en "
                "el territorio de la Republica Argentina.",
            ),
            (
                "4",
                "Confidencialidad",
                "Las partes se comprometen a mantener confidencialidad sobre toda informacion "
                "intercambiada durante la relacion contractual.",
            ),
        ],
    )


def create_adenda_simple() -> Image.Image:
    return draw_doc(
        "ADENDA NRO 1",
        "Modificacion simple - Marzo 2024",
        [
            (
                "2 modificada",
                "Nueva duracion del contrato",
                "Por acuerdo de partes, la vigencia del contrato se extiende a dieciocho (18) "
                "meses, quedando sin efecto el plazo de doce meses estipulado en la clausula 2 original.",
            ),
        ],
        color=(255, 255, 247),
        height=560,
    )


# ============================================================================
# Par 2 — Cambios complejos (contrato de confidencialidad)
# La adenda MODIFICA el territorio, ELIMINA la restriccion de uso, AGREGA una
# clausula nueva de difusion controlada. Tipos de cambio distintos.
# ============================================================================


def create_contrato_confidencialidad() -> Image.Image:
    return draw_doc(
        "CONTRATO DE CONFIDENCIALIDAD",
        "Version original - Febrero 2024",
        [
            (
                "1",
                "Alcance territorial",
                "Las partes acuerdan que la informacion confidencial cubierta por este contrato "
                "no podra ser utilizada fuera del territorio de la Republica Argentina.",
            ),
            (
                "2",
                "Restriccion de uso",
                "El receptor de la informacion confidencial se compromete a no utilizar dicha "
                "informacion para fines comerciales propios durante la vigencia del contrato ni "
                "durante los doce (12) meses posteriores a su finalizacion.",
            ),
            (
                "3",
                "Duracion del acuerdo",
                "El presente acuerdo de confidencialidad tendra una vigencia de veinticuatro (24) "
                "meses a partir de la fecha de firma.",
            ),
        ],
        color=(245, 250, 245),
    )


def create_adenda_compleja() -> Image.Image:
    return draw_doc(
        "ADENDA NRO 2",
        "Modificacion compleja - Julio 2024",
        [
            (
                "1 modificada",
                "Expansion del alcance territorial",
                "Por acuerdo de partes, el alcance territorial se amplia a los territorios de "
                "Argentina, Uruguay y Paraguay, quedando sin efecto la restriccion exclusiva "
                "al territorio argentino estipulada en la clausula 1 original.",
            ),
            (
                "2 eliminada",
                "Restriccion de uso",
                "Las partes acuerdan eliminar la clausula 2 del contrato original referida a la "
                "restriccion de uso de la informacion confidencial. La informacion podra ser "
                "utilizada por el receptor sin limitaciones temporales posteriores al contrato.",
            ),
            (
                "4 agregada",
                "Difusion controlada",
                "Se incorpora la siguiente clausula nueva: el receptor podra difundir la "
                "informacion confidencial a terceros subcontratistas, exclusivamente bajo "
                "acuerdo de confidencialidad previo firmado con cada subcontratista.",
            ),
        ],
        color=(255, 255, 247),
        height=780,
    )


def save_expected(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  OK {path.name}")


def main() -> None:
    print("Generando imagenes y golden datasets de PIM4...")

    # --- Par 1: Cambios simples ---
    print("\nPar 1 (simple):")
    create_contrato_servicios().save(
        PAIR1_DIR / "contrato_original.png", "PNG", dpi=(150, 150)
    )
    print("  OK contrato_original.png")
    create_adenda_simple().save(PAIR1_DIR / "adenda_simple.png", "PNG", dpi=(150, 150))
    print("  OK adenda_simple.png")
    save_expected(
        PAIR1_DIR / "expected.json",
        {
            "sections_changed": ["duration"],
            "topics_touched": ["duracion contractual"],
            "summary_of_the_change": "La duracion del contrato se extiende de 12 a 18 meses.",
        },
    )

    # --- Par 2: Cambios complejos ---
    print("\nPar 2 (complejo):")
    create_contrato_confidencialidad().save(
        PAIR2_DIR / "contrato_original.png", "PNG", dpi=(150, 150)
    )
    print("  OK contrato_original.png")
    create_adenda_compleja().save(
        PAIR2_DIR / "adenda_compleja.png", "PNG", dpi=(150, 150)
    )
    print("  OK adenda_compleja.png")
    save_expected(
        PAIR2_DIR / "expected.json",
        {
            "sections_changed": [
                "service_territory",
                "use_restriction",
                "controlled_disclosure",
            ],
            "topics_touched": [
                "alcance territorial",
                "restriccion de uso",
                "difusion controlada a terceros",
            ],
            "summary_of_the_change": (
                "Modificacion: el alcance territorial se amplia de Argentina a Argentina, "
                "Uruguay y Paraguay. Eliminacion: se remueve la clausula de restriccion "
                "de uso, permitiendo uso sin limite temporal. Adicion: se incorpora una "
                "clausula nueva de difusion controlada a subcontratistas bajo acuerdo previo."
            ),
        },
    )

    print(f"\nDataset PIM4 generado en: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
