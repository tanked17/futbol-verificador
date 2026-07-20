from dotenv import load_dotenv

load_dotenv()  # tiene que ir antes de importar los modulos que leen os.getenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import NewsInput, VerdictResponse
from app.services.ingestion import get_article_content
from app.services.groq_client import extract_claim, analyze_language
from app.services.football_data import check_match_result
from app.services.credibility import get_source_credibility
from app.services.verdict import build_verdict

app = FastAPI(title="Verificador de Noticias de Futbol")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://futbol-verificador.vercel.app",
        "http://localhost:5173",  # para seguir probando en local
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "service": "futbol-verificador-api"}


@app.post("/verify", response_model=VerdictResponse)
async def verify_news(payload: NewsInput):
    if not payload.text and not payload.url:
        raise HTTPException(status_code=400, detail="Debes enviar 'text' o 'url'.")

    try:
        content, source_domain = await get_article_content(payload)
        claim = await extract_claim(content)

        fact_check = None
        if claim.news_type == "resultado":
            fact_check = await check_match_result(claim)

        credibility = get_source_credibility(source_domain)
        linguistic = await analyze_language(content)

        return build_verdict(claim, fact_check, credibility, linguistic)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
