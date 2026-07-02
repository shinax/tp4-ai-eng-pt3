from pathlib import Path
from dotenv import load_dotenv
from langfuse import Langfuse
from agents import ChangeExtractorAgent, ContextualizationAgent
from image_parser import parse_contract_image
from models import ContractChangeOutput
import argparse

from utils import save_json

# Load environment variables
load_dotenv()

# Initialize Langfuse for tracing
langfuse_client = Langfuse()


def main():

    original_image ="./data/test_contracts/pair2_complex/contrato_original.png"
    amended_image ="./data/test_contracts/pair2_complex/adenda_compleja.png"

    parser = argparse.ArgumentParser(
        description="LegalMove PIM4 - Comparador de contratos con Vision y Agentes (produccion).",
    )
    parser.add_argument(
        "--original_path", type=str, default=original_image,
        help="Ruta a la imagen del contrato original (PNG/JPG/JPEG). Default: definido en el codigo.",
    )
    parser.add_argument(
        "--amendment_path", type=str, default=amended_image,
        help="Ruta a la imagen de la adenda (PNG/JPG/JPEG). Default: definido en el codigo.",
    )
    args = parser.parse_args()



    print("=" * 70)
    print("  LegalMove · Comparador de contratos (PRODUCCION)")
    print("=" * 70)
    print(f"  Contrato original : {Path(args.original_path).name}")
    print(f"  Adenda            : {Path(args.amendment_path).name}")
    
    
    trace_id = langfuse_client.create_trace_id()
    print(f"  Trace ID          : {trace_id}")
    # Process the images
    result_image_1 = parse_contract_image(args.original_path, image_label="original_image", trace_id=trace_id, langfuse_client=langfuse_client)
    result_image_2 = parse_contract_image(args.amendment_path, image_label="amended_image", trace_id=trace_id, langfuse_client=langfuse_client)
    
    # Contextualización de los resultados para la comparación
    contextualizer = ContextualizationAgent(langfuse_client=langfuse_client,)
    mapa_contextual = contextualizer.build_context_map(analysis_1=result_image_1, analysis_2=result_image_2, trace_id=trace_id)

    # Extraer los cambios y diferencias entre los documentos
    change_extractor = ChangeExtractorAgent(langfuse_client=langfuse_client)
    changes = change_extractor.extract_changes(result_image_1, result_image_2, mapa_contextual, trace_id=trace_id)

    # Validar
    try:
        validated_output = ContractChangeOutput.validate_output(changes)

        print("\n" + "=" * 70)
        print("  RESULTADO — Cambios detectados en la adenda")
        print("=" * 70)
        print("  Secciones : " + ", ".join(validated_output.sections_changed))
        print("  Temas     : " + ", ".join(validated_output.topics_touched))
        print("  Resumen   : " + validated_output.summary_of_the_change)

        save_json(
            data=validated_output.model_dump(),
            trace_id=trace_id
        )
    except ValueError as e:
        print(f"❌ Error de validación: {e}")
    finally:
        # Flush Langfuse traces
        langfuse_client.flush()
        print("📡 Trazas enviadas a Langfuse")

    


if __name__ == "__main__":
    main()
