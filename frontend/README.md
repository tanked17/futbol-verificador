# Offside — Frontend

Interfaz para pegar una noticia (texto o URL) y ver el veredicto del backend,
con la evidencia desglosada (fact-check, credibilidad de fuente, señales de
lenguaje).

## Setup en Windows

Necesitás el backend corriendo en paralelo (`http://127.0.0.1:8000` por
defecto).

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

Se abre en `http://localhost:5173`. Si corrés el backend en otro puerto o
dominio, cambiá `VITE_API_URL` en `.env`.

## Diseño

Paleta y tipografía pensadas para que se sienta a "cancha de noche" más que a
dashboard genérico: fondo verde-carbón, tarjeta de veredicto con color tipo
tarjeta arbitral (verde/amarillo/rojo) y lectura de confianza en formato
scoreboard (`JetBrains Mono`, números tabulares). Encabezados en `Anton`
(condensada, tipo cartel de estadio), cuerpo en `Inter`.

## Deploy

Igual que Mundial Asistente: `npm run build` genera `dist/`, listo para
desplegar en Vercel. Acordate de configurar `VITE_API_URL` como variable de
entorno en Vercel apuntando a tu backend deployado en Render.
