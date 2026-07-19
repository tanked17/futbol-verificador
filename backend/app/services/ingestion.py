import trafilatura
from urllib.parse import urlparse

from app.models import NewsInput


async def get_article_content(payload: NewsInput):
    """
    Devuelve (contenido_de_texto, dominio_origen).
    Si viene texto/tweet pegado directamente, dominio_origen es None
    (no hay forma de puntuar credibilidad de fuente sin URL, salvo
    que mas adelante detectemos el @handle si es un tweet).
    """
    if payload.url:
        downloaded = trafilatura.fetch_url(payload.url)
        if not downloaded:
            raise ValueError("No se pudo acceder a la URL proporcionada.")

        text = trafilatura.extract(downloaded)
        if not text:
            raise ValueError("No se pudo extraer contenido legible de esa URL.")

        domain = urlparse(payload.url).netloc.replace("www.", "")
        return text, domain

    if payload.text:
        return payload.text.strip(), None

    raise ValueError("Debes enviar 'text' o 'url'.")
