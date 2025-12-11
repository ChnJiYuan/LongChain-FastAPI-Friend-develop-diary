export type ChatRequest = {
  userId: string
  message: string
}

export type ChatResponse = {
  reply: string
  memori_context?: string
  milvus_chunks?: string[]
}

export async function sendChat(baseUrl: string, payload: ChatRequest, apiKey?: string): Promise<ChatResponse> {
  const resolvedKey = (apiKey ?? import.meta.env.VITE_API_KEY)?.trim()
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (resolvedKey) {
    headers['X-API-Key'] = resolvedKey
  }

  const res = await fetch(`${baseUrl}/api/v1/chat`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ user_id: payload.userId, message: payload.message }),
  })

  if (!res.ok) {
    throw new Error(`Chat API failed with status ${res.status}`)
  }

  return res.json()
}
