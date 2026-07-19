# Offside — Verificador de noticias de fútbol

Proyecto en dos partes: `backend/` (FastAPI, pipeline de verificación) y
`frontend/` (React + Vite, interfaz para probarlo).

## Correr todo en local (Windows)

**Terminal 1 — backend:**
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# completá GROQ_API_KEY y FOOTBALL_DATA_API_KEY en .env
py -m uvicorn main:app --reload
```

**Terminal 2 — frontend:**
```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

Abrí `http://localhost:5173`, pegá una noticia de fútbol (texto o URL), y
deberías ver el veredicto completo con su evidencia.

Ver `backend/README.md` y `frontend/README.md` para el detalle de cada parte,
estado actual de cada módulo, y próximos pasos sugeridos.
