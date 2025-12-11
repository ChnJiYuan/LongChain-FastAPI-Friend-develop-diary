import { FormEvent, useMemo, useState } from 'react'
import './App.css'
import { sendChat } from './api/client'

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

  const disabled = useMemo(() => loading || !message.trim(), [loading, message])

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

  return (
    <div className="app">
      <header className="app__header">
        <div>
          <p className="eyebrow">Membot</p>
          <h1>Chat with dual memory</h1>
          <p className="subhead">Memori for structured facts; Milvus for vector recall.</p>
        </div>
        <div className="pill">API: {resolvedApiBase}</div>
      </header>

      <main className="layout">
        <section className="chat">
          <form className="chat__form" onSubmit={handleSubmit}>
            <label className="label">
              User ID
              <input
                aria-label="User ID"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                placeholder="user-123"
              />
            </label>
            <label className="label">
              Message
              <textarea
                aria-label="Message"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ask me anything..."
                rows={3}
              />
            </label>
            <button type="submit" disabled={disabled}>
              {loading ? 'Sending...' : 'Send'}
            </button>
            {error && <p className="error" role="alert">{error}</p>}
          </form>

          <div className="chat__history" aria-label="Chat history">
            {history.length === 0 ? (
              <p className="muted">No messages yet.</p>
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

        <aside className="context">
          <h2>Retrieved context</h2>
          <div className="context__block">
            <h3>Memori</h3>
            <pre>{memoriContext || 'No Memori context yet.'}</pre>
          </div>
          <div className="context__block">
            <h3>Milvus</h3>
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
        </aside>
      </main>
    </div>
  )
}

export default App
