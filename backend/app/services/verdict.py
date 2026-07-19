from typing import Optional

from app.models import (
    ClaimExtraction,
    FactCheckResult,
    CredibilityResult,
    LinguisticAnalysis,
    VerdictResponse,
)


def build_verdict(
    claim: ClaimExtraction,
    fact_check: Optional[FactCheckResult],
    credibility: CredibilityResult,
    linguistic: LinguisticAnalysis,
) -> VerdictResponse:
    breakdown = {
        "tipo_detectado": claim.news_type,
        "afirmacion_central": claim.central_claim,
        "entidades": claim.entities,
        "fact_check": fact_check.dict() if fact_check else {"checked": False},
        "credibilidad_fuente": credibility.dict(),
        "analisis_lenguaje": linguistic.dict(),
    }

    # 1. Si hubo verificacion dura y fue concluyente, ese dato manda por sobre todo lo demas.
    if fact_check and fact_check.checked and fact_check.matches_data is not None:
        if fact_check.matches_data:
            return VerdictResponse(
                verdict="Confirmado",
                confidence=95,
                explanation="El hecho coincide con datos oficiales verificados.",
                breakdown=breakdown,
            )
        return VerdictResponse(
            verdict="Contradice datos verificados",
            confidence=90,
            explanation="El hecho no coincide con los datos oficiales consultados.",
            breakdown=breakdown,
        )

    # 2. Sin dato duro: combinar credibilidad de la fuente con señales de lenguaje.
    fake_signal = linguistic.score       # 0-100, mas alto = mas sospechoso
    trust_signal = credibility.score     # 0-100, mas alto = fuente mas confiable

    combined = trust_signal - (fake_signal * 0.4)

    if combined >= 65:
        verdict, confidence, explanation = (
            "Reportado por fuente confiable",
            min(85, combined),
            "La fuente tiene buen historial y el texto no muestra señales claras de manipulacion.",
        )
    elif combined >= 30:
        verdict, confidence, explanation = (
            "Rumor sin confirmar",
            60,
            "No hay datos oficiales que lo respalden ni lo contradigan; tratar con cautela.",
        )
    else:
        verdict, confidence, explanation = (
            "Probablemente engañoso",
            min(80, 100 - combined),
            "Fuente de baja credibilidad y/o lenguaje con señales de sensacionalismo.",
        )

    return VerdictResponse(verdict=verdict, confidence=confidence, explanation=explanation, breakdown=breakdown)
