import json
import os
from typing import Optional

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "trusted_sources.json")

with open(DATA_PATH, encoding="utf-8") as f:
    _SOURCES = json.load(f)

_LEVEL_SCORES = {"alto": 90, "medio": 60, "bajo": 15, "desconocido": 50}


def get_source_credibility(domain_or_handle: Optional[str]):
    from app.models import CredibilityResult

    if not domain_or_handle:
        return CredibilityResult(source=None, level="desconocido", score=_LEVEL_SCORES["desconocido"])

    key = domain_or_handle.lower().replace("www.", "")

    for level in ("alto", "medio", "bajo"):
        candidates = [s.lower() for s in _SOURCES.get(level, [])]
        if key in candidates:
            return CredibilityResult(source=key, level=level, score=_LEVEL_SCORES[level])

    return CredibilityResult(source=key, level="desconocido", score=_LEVEL_SCORES["desconocido"])
