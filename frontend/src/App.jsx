import { useState } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const PIPELINE_STEPS = [
  { title: 'Ingesta', desc: 'Lee el texto pegado o extrae el artículo completo desde la URL.' },
  { title: 'Extracción de la afirmación', desc: 'Identifica de qué tipo de noticia se trata y cuál es el dato central a chequear.' },
  { title: 'Fact-check', desc: 'Si es un resultado de partido, lo contrasta contra datos oficiales de football-data.org.' },
  { title: 'Credibilidad de la fuente', desc: 'Evalúa el dominio o medio de origen contra una base curada de fuentes.' },
  { title: 'Señales de lenguaje', desc: 'Busca sensacionalismo, falta de fuentes citadas y contradicciones internas.' },
  { title: 'Veredicto', desc: 'Combina todas las señales en un resultado con la evidencia a la vista.' },
]

function verdictStyle(verdict) {
  if (verdict === 'Confirmado' || verdict === 'Reportado por fuente confiable') {
    return { modifier: 'confirmado' }
  }
  if (verdict === 'Contradice datos verificados' || verdict === 'Probablemente engañoso') {
    return { modifier: 'enganoso' }
  }
  return { modifier: 'rumor' }
}

export default function App() {
  const [mode, setMode] = useState('text')
  const [textValue, setTextValue] = useState('')
  const [urlValue, setUrlValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const currentValue = mode === 'text' ? textValue : urlValue
  const canSubmit = currentValue.trim().length > 0 && !loading

  async function handleSubmit(e) {
    e.preventDefault()
    if (!canSubmit) return

    setLoading(true)
    setError(null)
    setResult(null)

    const payload = mode === 'text' ? { text: textValue.trim() } : { url: urlValue.trim() }

    try {
      const res = await fetch(`${API_URL}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || 'No se pudo verificar la noticia.')
      }

      setResult(data)
    } catch (err) {
      setError(
        err.message === 'Failed to fetch'
          ? `No se pudo conectar con el servidor (${API_URL}). Revisá que el backend esté corriendo.`
          : err.message
      )
    } finally {
      setLoading(false)
    }
  }

  const style = result ? verdictStyle(result.verdict) : null
  const factCheck = result?.breakdown?.fact_check
  const credibility = result?.breakdown?.credibilidad_fuente
  const linguistic = result?.breakdown?.analisis_lenguaje

  return (
    <div className="app">
      <div className="app__inner">
        <header className="app__header">
          <p className="app__eyebrow">Verificador · Fútbol</p>
          <h1 className="app__title">Pega la noticia.<br />Te decimos si es de fiar.</h1>
          <p className="app__subtitle">
            Fichajes, resultados, declaraciones y rumores. Cruzamos datos oficiales,
            credibilidad de la fuente y análisis de lenguaje para darte un veredicto
            con la evidencia a la vista, no un simple sí o no.
          </p>
        </header>

        <form className="app__form" onSubmit={handleSubmit}>
          <div className="form__toggle" role="tablist" aria-label="Tipo de entrada">
            <button
              type="button"
              role="tab"
              aria-selected={mode === 'text'}
              className={`form__toggle-btn ${mode === 'text' ? 'is-active' : ''}`}
              onClick={() => setMode('text')}
            >
              Texto o tweet
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={mode === 'url'}
              className={`form__toggle-btn ${mode === 'url' ? 'is-active' : ''}`}
              onClick={() => setMode('url')}
            >
              URL
            </button>
          </div>

          {mode === 'text' ? (
            <textarea
              className="form__textarea"
              placeholder="Pega aquí el texto de la noticia o el tweet que quieres verificar…"
              value={textValue}
              onChange={(e) => setTextValue(e.target.value)}
              aria-label="Texto de la noticia"
            />
          ) : (
            <input
              className="form__input"
              type="url"
              placeholder="https://ejemplo.com/noticia-de-futbol"
              value={urlValue}
              onChange={(e) => setUrlValue(e.target.value)}
              aria-label="URL de la noticia"
            />
          )}

          <div className="form__footer">
            <span className="form__hint">El análisis tarda unos segundos.</span>
            <button className="form__submit" type="submit" disabled={!canSubmit}>
              {loading ? 'Verificando…' : 'Verificar'}
            </button>
          </div>

          {error && <p className="form__error">{error}</p>}
        </form>

        {result && (
          <section className="result">
            <div className={`result__card result__card--${style.modifier}`}>
              <div className="result__top">
                <h2 className="result__verdict">{result.verdict}</h2>
                <div className="result__confidence">
                  <span className="result__confidence-value">{Math.round(result.confidence)}%</span>
                  <span className="result__confidence-label">Confianza</span>
                </div>
              </div>

              <p className="result__explanation">{result.explanation}</p>

              <div className="result__evidence">
                {result.breakdown?.tipo_detectado && (
                  <div className="evidence__item">
                    <span className="evidence__label">Tipo</span>
                    <span className="evidence__value">{result.breakdown.tipo_detectado}</span>
                  </div>
                )}

                {factCheck && (
                  <div className="evidence__item">
                    <span className="evidence__label">Fact-check</span>
                    <span className="evidence__value">
                      {factCheck.checked ? factCheck.detail : (factCheck.detail || 'No aplica a este tipo de noticia.')}
                    </span>
                  </div>
                )}

                {credibility && (
                  <div className="evidence__item">
                    <span className="evidence__label">Fuente</span>
                    <span className="evidence__value">
                      {credibility.source || 'No especificada'} · credibilidad {credibility.level} ({Math.round(credibility.score)}/100)
                    </span>
                  </div>
                )}

                {linguistic && (
                  <div className="evidence__item">
                    <span className="evidence__label">Lenguaje</span>
                    <span className="evidence__value">
                      {linguistic.red_flags?.length ? (
                        <span className="evidence__chips">
                          {linguistic.red_flags.map((flag) => (
                            <span className="chip" key={flag}>{flag}</span>
                          ))}
                        </span>
                      ) : (
                        'Sin señales de manipulación detectadas.'
                      )}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </section>
        )}

        <section className="pipeline">
          <p className="pipeline__title">Cómo lo verificamos</p>
          <div className="pipeline__list">
            {PIPELINE_STEPS.map((step, i) => (
              <div className="pipeline__step" key={step.title}>
                <span className="pipeline__number">{String(i + 1).padStart(2, '0')}</span>
                <div>
                  <p className="pipeline__step-title">{step.title}</p>
                  <p className="pipeline__step-desc">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <footer className="app__footer">
          Offside no reemplaza el periodismo verificado — es una primera capa de chequeo.
        </footer>
      </div>
    </div>
  )
}
