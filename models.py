from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, ValidationError


class ContractChangeOutput(BaseModel):
    """Modelo para el output validado del ChangeExtractorAgent"""
    sections_changed: list[str] = Field(
        description="Palabras cortas que sirvan como identificadores de las secciones modificadas (ej: payment_terms, duration, service_territory, use_restriction)")
    topics_touched: list[str] = Field(
        description="Categorías legales/comerciales afectadas (ej: Plazo, Pago, Responsabilidad, etc.)")
    summary_of_the_change: str = Field(
        description="Descripción detallada y comprehensiva de todos los cambios realizados en la enmienda")

    @field_validator("sections_changed", "topics_touched")
    @classmethod
    def non_empty_list(cls, value: list[str]) -> list[str]:
        """Valida que las listas efectivamente tengan contenido.
        """
        if not value:
            raise ValueError("La lista no puede estar vacía; la adenda debe afectar al menos una sección.")
        if any(not item.strip() for item in value):
            raise ValueError("Los valores de la lista no pueden ser strings vacíos.")
        return value

    @staticmethod
    def validate_output(payload: dict) -> ContractChangeOutput:
        try:
            return ContractChangeOutput.model_validate(payload)
        except ValidationError as exc:
            print(payload)
            raise ValueError(f"El input no cumple con el formato requerido para generar un objeto ContractChangeOutput: {exc}") from exc