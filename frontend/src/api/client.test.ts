import { afterEach, describe, expect, it, vi } from 'vitest'

import { sendChat } from './client'

afterEach(() => {
  vi.restoreAllMocks()
})

describe('sendChat', () => {
  it('posts to chat endpoint and returns parsed response', async () => {
    const mockResponse = {
      reply: 'hi there',
      memori_context: 'profile block',
      milvus_chunks: ['c1'],
    }

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: vi.fn().mockResolvedValue(mockResponse),
    })
    vi.stubGlobal('fetch', fetchMock)

    const result = await sendChat('http://api.local', { userId: 'u1', message: 'hello' })

    expect(result).toEqual(mockResponse)
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.local/api/v1/chat',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      }),
    )
  })

  it('throws on non-2xx responses', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: vi.fn(),
    })
    vi.stubGlobal('fetch', fetchMock)

    await expect(sendChat('http://api.local', { userId: 'u1', message: 'hello' })).rejects.toThrow(
      /500/,
    )
  })
})
