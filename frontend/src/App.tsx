import { useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import './App.css'
import { generateImage, sendChat } from './api/client'

type ChatMessage = {
  role: 'user' | 'assistant'
  content: string
}

type AppProps = {
  apiBase?: string
}

function App({ apiBase }: AppProps = {}) {
  const resolvedApiBase = apiBase ?? import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
  const [userId, setUserId] = useState('demo-user')
  const [message, setMessage] = useState('')
  const [history, setHistory] = useState<ChatMessage[]>([])
  const [memoriContext, setMemoriContext] = useState<string | null>(null)
  const [milvusChunks, setMilvusChunks] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [imagePrompt, setImagePrompt] = useState('')
  const [imageResult, setImageResult] = useState<string | null>(null)
  const [imageProvider, setImageProvider] = useState<string | null>(null)
  const [imageLoading, setImageLoading] = useState(false)
  const [imageError, setImageError] = useState<string | null>(null)

  const disabled = useMemo(() => loading || !message.trim(), [loading, message])
  const stats = useMemo(
    () => ({
      turns: history.length,
      milvusHits: milvusChunks.length,
      hasMemori: Boolean(memoriContext),
    }),
    [history.length, milvusChunks.length, memoriContext],
  )

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!message.trim()) return
    setLoading(true)
    setError(null)
    const userMsg = message
    setHistory((prev) => [...prev, { role: 'user', content: userMsg }])
    setMessage('')

    try {
      const res = await sendChat(resolvedApiBase, { userId, message: userMsg })
      setHistory((prev) => [...prev, { role: 'assistant', content: res.reply }])
      setMemoriContext(res.memori_context ?? null)
      setMilvusChunks(res.milvus_chunks ?? [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  const handleImage = async (e: FormEvent) => {
    e.preventDefault()
    if (!imagePrompt.trim()) return
    setImageLoading(true)
    setImageError(null)
    setImageResult(null)
    setImageProvider(null)
    try {
      const res = await generateImage(resolvedApiBase, { prompt: imagePrompt })
      setImageResult(res.image_base64)
      setImageProvider(res.provider)
    } catch (err) {
      setImageError(err instanceof Error ? err.message : 'Image request failed')
    } finally {
      setImageLoading(false)
    }
  }

  return (
    <div className="page">
      <div className="halo" aria-hidden="true" />
      <div className="content">
        <header className="hero">
          <div className="badge-row">
            <span className="badge">Membot</span>
            <span className="pill">API: {resolvedApiBase}</span>
          </div>
          <div className="headline">
            <div>
              <p className="eyebrow">Dual memory surface</p>
              <h1>Chat with dual memory</h1>
              <p className="subhead">Memori holds structured facts; Milvus brings semantic recall.</p>
            </div>
            <div className="stat-row">
              <div className="stat">
                <span className="stat__label">Turns</span>
                <span className="stat__value">{stats.turns}</span>
              </div>
              <div className="stat">
                <span className="stat__label">Milvus hits</span>
                <span className="stat__value">{stats.milvusHits}</span>
              </div>
              <div className="stat">
                <span className="stat__label">Memori</span>
                <span className={`stat__dot ${stats.hasMemori ? 'stat__dot--on' : ''}`} />
                <span className="stat__value">{stats.hasMemori ? 'hydrated' : 'pending'}</span>
              </div>
            </div>
          </div>
        </header>

        <main className="layout">
          <section className="panel panel--chat">
            <form className="chat__form" onSubmit={handleSubmit}>
              <div className="input-grid">
                <label className="label">
                  User ID
                  <input
                    aria-label="User ID"
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    placeholder="user-123"
                  />
                </label>
                <label className="label label--grow">
                  Message
                  <textarea
                    aria-label="Message"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Ask me anything..."
                    rows={3}
                  />
                </label>
              </div>
              <div className="form-footer">
                <button type="submit" disabled={disabled}>
                  {loading ? 'Sending...' : 'Send'}
                </button>
                {error && <p className="error" role="alert">{error}</p>}
              </div>
            </form>

            <div className="chat__history" aria-label="Chat history">
              {history.length === 0 ? (
                <p className="muted">No messages yet. Start the first turn.</p>
              ) : (
                history.map((msg, idx) => (
                  <div key={idx} className={`bubble bubble--${msg.role}`}>
                    <span className="bubble__role">{msg.role}</span>
                    <p>{msg.content}</p>
                  </div>
                ))
              )}
            </div>
          </section>

          <aside className="panel panel--context">
            <h2>Retrieved context</h2>
            <div className="context__block">
              <div className="context__header">
                <h3>Memori</h3>
                <span className={`chip ${memoriContext ? 'chip--on' : ''}`}>
                  {memoriContext ? 'Ready' : 'Waiting'}
                </span>
              </div>
              <pre>{memoriContext || 'No Memori context yet.'}</pre>
            </div>
            <div className="context__block">
              <div className="context__header">
                <h3>Milvus</h3>
                <span className="chip chip--ghost">{milvusChunks.length} hit(s)</span>
              </div>
              {milvusChunks.length === 0 ? (
                <p className="muted">No Milvus hits yet.</p>
              ) : (
                <ul>
                  {milvusChunks.map((chunk, i) => (
                    <li key={i}>{chunk}</li>
                  ))}
                </ul>
              )}
            </div>
            <div className="context__block">
              <div className="context__header">
                <h3>Image</h3>
                <span className="chip chip--ghost">{imageProvider || 'Idle'}</span>
              </div>
              <form className="image__form" onSubmit={handleImage}>
                <input
                  aria-label="Image prompt"
                  value={imagePrompt}
                  onChange={(e) => setImagePrompt(e.target.value)}
                  placeholder="Describe an image to generate"
                />
                <button type="submit" disabled={imageLoading || !imagePrompt.trim()}>
                  {imageLoading ? 'Generating...' : 'Generate'}
                </button>
              </form>
              {imageError && <p className="error" role="alert">{imageError}</p>}
              <div className="image__preview">
                {imageResult ? (
                  <img src={`data:image/png;base64,${imageResult}`} alt="Generated" />
                ) : (
                  <p className="muted">No image yet.</p>
                )}
              </div>
            </div>
          </aside>
        </main>
      </div>
    </div>
  )
}

export default App
