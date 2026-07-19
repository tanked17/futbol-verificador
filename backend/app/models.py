from typing import Optional, List, Dict
from pydantic import BaseModel


class NewsInput(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None


class ClaimExtraction(BaseModel):
    news_type: str  # fichaje, resultado, declaracion, rumor, lesion, otro
    entities: List[str] = []
    entities_en: List[str] = []
    central_claim: str
    mentioned_date: Optional[str] = None
    claimed_home_score: Optional[int] = None
    claimed_away_score: Optional[int] = None


class FactCheckResult(BaseModel):
    checked: bool
    matches_data: Optional[bool] = None
    detail: str = ""


class CredibilityResult(BaseModel):
    source: Optional[str] = None
    level: str  # alto, medio, bajo, desconocido
    score: float


class LinguisticAnalysis(BaseModel):
    score: float  # 0-100, mas alto = mas señales de fake news
    red_flags: List[str] = []


class VerdictResponse(BaseModel):
    verdict: str
    confidence: float
    explanation: str
    breakdown: Dict
