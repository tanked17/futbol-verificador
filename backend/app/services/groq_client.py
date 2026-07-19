import os
import json
import httpx

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"


async def _call_groq(system_prompt: str, user_content: str) -> dict:
    if not GROQ_API_KEY:
        raise RuntimeError("Falta GROQ_API_KEY en el entorno (.env).")

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
            },
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"]
        return json.loads(raw)


async def extract_claim(text: str):
    from app.models import ClaimExtraction

    system = (
        "Sos un analista de noticias de futbol. Dado un texto, respondes SOLO con un JSON "
        "(sin markdown, sin texto extra) con estas claves exactas: "
        '"news_type" (uno de: fichaje, resultado, declaracion, rumor, lesion, otro), '
        '"entities" (lista de nombres de jugadores/equipos/competiciones mencionados, tal como '
        "aparecen en el texto original), "
        '"entities_en" (los mismos equipos/selecciones pero traducidos a su nombre oficial en '
        "ingles, por ejemplo 'Francia' -> 'France', 'Inglaterra' -> 'England'; si ya estan en "
        "ingles o no aplica, repetilos igual), "
        '"central_claim" (la afirmacion principal del texto en una oracion), '
        '"mentioned_date" (fecha mencionada en el texto si la hay, sino null), '
        '"claimed_home_score" y "claimed_away_score" (SOLO si news_type es "resultado": los goles '
        "del equipo que jugo de local y del visitante, como numeros enteros, buscando el marcador "
        "en cualquier parte del texto aunque este escrito con palabras tipo 'seis a cuatro'; si no "
        "es un resultado o no encontras un marcador claro, ambos van en null)."
    )
    data = await _call_groq(system, text[:4000])
    return ClaimExtraction(**data)


async def analyze_language(text: str):
    from app.models import LinguisticAnalysis

    system = (
        "Sos un detector de señales de fake news en textos deportivos. Respondes SOLO con un JSON "
        '(sin markdown, sin texto extra) con: "score" (numero 0-100, donde 100 es maxima '
        'probabilidad de fake news segun el lenguaje usado) y "red_flags" (lista corta de señales '
        "detectadas en español, por ejemplo 'lenguaje sensacionalista', 'sin fuente citada', "
        "'contradiccion interna', 'titulo no coincide con el contenido'). Si no detectas señales, "
        "devolve red_flags vacio y score bajo (0-20)."
    )
    data = await _call_groq(system, text[:4000])
    return LinguisticAnalysis(**data)
