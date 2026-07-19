# Verificador de Noticias de Fútbol — Backend

Pipeline de 6 módulos para evaluar si una noticia de fútbol (texto pegado o URL)
es confiable, un rumor sin confirmar, o probablemente engañosa.

## Estado actual (MVP scaffold)

| Módulo | Estado |
|---|---|
| 1. Ingesta (texto + URL) | ✅ Funcional |
| 2. Extracción de claims (Groq) | ✅ Funcional (necesita `GROQ_API_KEY`) |
| 3. Fact-check resultados (football-data.org) | ✅ Funcional (necesita `FOOTBALL_DATA_API_KEY`) — matchea equipo por nombre tolerante a variaciones y compara marcador |
| 4. Credibilidad de fuentes | ✅ Funcional, pero la lista en `app/data/trusted_sources.json` es solo un punto de partida — hay que ampliarla |
| 5. Análisis lingüístico (Groq) | ✅ Funcional (necesita `GROQ_API_KEY`) |
| 6. Motor de veredicto | ✅ Funcional |

Nota sobre fichajes: `football-data.org` no tiene datos de mercado de
transferencias, solo resultados/calendarios/planteles. Por eso los fichajes
dependen hoy 100% del módulo de credibilidad de fuente (paso 4), no de un
fact-check contra datos duros. Si más adelante querés verificar fichajes con
dato duro, hay que sumar otra fuente (API-Football tiene endpoint de
transfers, de pago para volumen alto).

## Setup en Windows

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Editá `.env` y completá:
- `GROQ_API_KEY` → sacala de https://console.groq.com (mismo que usaste en Mundial Asistente)
- `FOOTBALL_DATA_API_KEY` → sacala de https://www.football-data.org

Correr el servidor:

```powershell
py -m uvicorn main:app --reload
```

Probar:

```powershell
curl http://127.0.0.1:8000/
```

## Endpoint principal

`POST /verify`

```json
{ "text": "Mbappé fue fichado por el Real Madrid según fuentes cercanas" }
```
o
```json
{ "url": "https://ejemplo.com/noticia" }
```

Devuelve un veredicto (`Confirmado`, `Reportado por fuente confiable`,
`Rumor sin confirmar`, `Contradice datos verificados`, `Probablemente
engañoso`) con un `breakdown` que muestra toda la evidencia usada — nunca un
simple sí/no, para que el usuario vea el razonamiento.

## Próximos pasos sugeridos

1. Ampliar `app/data/trusted_sources.json` con más medios y cuentas de X
   verificadas (Fabrizio Romano, David Ornstein, etc.) — hoy la handle de
   Twitter/X no se está capturando desde texto pegado, solo dominios de URL.
2. Frontend en React + Vite (igual stack que Mundial Asistente) con input de
   texto/URL y visualización del breakdown.
3. Deploy en Render (backend) + Vercel (frontend), como en tu proyecto
   anterior.

## Limitación conocida del fact-check de resultados

La extracción del marcador afirmado (`_extract_claimed_score` en
`football_data.py`) usa una expresión regular que busca un patrón "N-N" en
`central_claim`. Si el texto describe el resultado sin usar ese formato
(ej. "Real Madrid goleó a su rival"), no hay marcador que comparar y el
fact-check devuelve `checked=False` en vez de forzar una comparación. Es una
limitación aceptable para el MVP; si hace falta más precisión, se puede pedirle
a Groq que devuelva el marcador como campos estructurados en vez de extraerlo
por regex del texto libre.
