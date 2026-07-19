import os
import re
import unicodedata
from datetime import date, timedelta
from typing import Optional, Tuple

import httpx

from app.models import FactCheckResult, ClaimExtraction

FOOTBALL_DATA_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4"

# NOTA: football-data.org cubre resultados/calendarios/planteles, NO datos de
# mercado de fichajes. Por eso esta verificacion con dato duro solo aplica a
# noticias de tipo "resultado"; los fichajes siguen dependiendo del modulo de
# credibilidad de fuente (services/credibility.py).


def _normalize(name: str) -> str:
    """Saca acentos, sufijos comunes (FC, CF, etc.) y deja solo alfanumerico
    en minuscula, para poder comparar nombres de equipos de forma tolerante."""
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    name = re.sub(r"\b(fc|cf|cd|sad|club|de|futbol|f\.c\.)\b", "", name.lower())
    return re.sub(r"[^a-z0-9]", "", name)


def _team_matches(entity: str, team_name: str, short_name: Optional[str] = None, tla: Optional[str] = None) -> bool:
    ent = _normalize(entity)
    if not ent:
        return False
    for candidate in (team_name, short_name or "", tla or ""):
        norm_c = _normalize(candidate)
        if norm_c and (ent in norm_c or norm_c in ent):
            return True
    return False


def _extract_claimed_score(text: str) -> Optional[Tuple[int, int]]:
    """Heuristica simple: busca un patron 'N-N' en la afirmacion central
    (ej. 'Real Madrid gano 3-1 a Barcelona'). Si el texto no trae el
    marcador en ese formato, devuelve None y el fact-check queda sin
    poder comparar el resultado exacto."""
    match = re.search(r"(\d+)\s*[-–:]\s*(\d+)", text)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


async def check_match_result(claim: ClaimExtraction) -> FactCheckResult:
    if claim.news_type != "resultado":
        return FactCheckResult(
            checked=False,
            detail="Tipo de noticia no verificable contra datos de partidos (solo aplica a 'resultado').",
        )

    if not FOOTBALL_DATA_KEY:
        return FactCheckResult(checked=False, detail="Falta FOOTBALL_DATA_API_KEY en el entorno (.env).")

    if claim.mentioned_date:
        try:
            center = date.fromisoformat(claim.mentioned_date[:10])
        except ValueError:
            center = date.today()
    else:
        center = date.today()

    date_from = center - timedelta(days=2)
    date_to = center + timedelta(days=1)

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{BASE_URL}/matches",
            headers={"X-Auth-Token": FOOTBALL_DATA_KEY},
            params={"dateFrom": date_from.isoformat(), "dateTo": date_to.isoformat()},
        )
        if resp.status_code != 200:
            return FactCheckResult(
                checked=False,
                detail=f"No se pudo consultar football-data.org (status {resp.status_code}).",
            )
        matches = resp.json().get("matches", [])

    if not matches:
        return FactCheckResult(
            checked=False,
            detail="No se encontraron partidos en el rango de fechas estimado para contrastar.",
        )

    # Preferimos entities_en porque football-data.org devuelve nombres en ingles;
    # si por algun motivo vino vacio, caemos de nuevo a entities tal cual.
    entities = claim.entities_en or claim.entities or []
    found = None
    for m in matches:
        home = m.get("homeTeam", {}) or {}
        away = m.get("awayTeam", {}) or {}
        home_hit = any(_team_matches(e, home.get("name", ""), home.get("shortName"), home.get("tla")) for e in entities)
        away_hit = any(_team_matches(e, away.get("name", ""), away.get("shortName"), away.get("tla")) for e in entities)
        if home_hit and away_hit:
            found = m
            break

    if not found:
        return FactCheckResult(
            checked=False,
            detail="No se encontro un partido que coincida con los equipos mencionados en ese rango de fechas.",
        )

    status = found.get("status")
    if status != "FINISHED":
        return FactCheckResult(
            checked=False,
            detail=f"Se encontro el partido pero su estado es '{status}', todavia no hay resultado final para contrastar.",
        )

    full_time = (found.get("score", {}) or {}).get("fullTime", {}) or {}
    real_home, real_away = full_time.get("home"), full_time.get("away")

    if claim.claimed_home_score is not None and claim.claimed_away_score is not None:
        claimed = (claim.claimed_home_score, claim.claimed_away_score)
    else:
        claimed = _extract_claimed_score(claim.central_claim)

    if claimed is None:
        return FactCheckResult(
            checked=False,
            detail=f"Se encontro el partido (resultado real {real_home}-{real_away}) pero no se pudo extraer un marcador claro de la afirmacion para comparar.",
        )

    matches_data = claimed == (real_home, real_away) or claimed == (real_away, real_home)
    return FactCheckResult(
        checked=True,
        matches_data=matches_data,
        detail=f"Resultado real: {real_home}-{real_away}. Marcador afirmado en la noticia: {claimed[0]}-{claimed[1]}.",
    )
