import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import App from './App'
import * as api from './api/client'

describe('App chat flow', () => {
  beforeEach(() => {
    ;(import.meta as any).env = { VITE_API_BASE_URL: 'http://api.local' }
  })

  it('sends a message and renders reply and contexts', async () => {
    const sendChatMock = vi.spyOn(api, 'sendChat').mockResolvedValue({
      reply: 'Hello!',
      memori_context: 'Profile: demo',
      milvus_chunks: ['similar text'],
    })

    render(<App apiBase="http://api.local" />)

    fireEvent.change(screen.getByLabelText(/User ID/i), { target: { value: 'u1' } })
    fireEvent.change(screen.getByLabelText(/Message/i), { target: { value: 'Hi bot' } })
    fireEvent.click(screen.getByRole('button', { name: /send/i }))

    await waitFor(() => expect(sendChatMock).toHaveBeenCalled())
    expect(sendChatMock).toHaveBeenCalledWith('http://api.local', { userId: 'u1', message: 'Hi bot' })

    await screen.findByText('Hello!')
    expect(screen.getByText(/Profile: demo/)).toBeInTheDocument()
    expect(screen.getByText('similar text')).toBeInTheDocument()
  })

  it('shows error when request fails', async () => {
    vi.spyOn(api, 'sendChat').mockRejectedValue(new Error('boom'))
    render(<App apiBase="http://api.local" />)

    fireEvent.change(screen.getByLabelText(/Message/i), { target: { value: 'test' } })
    fireEvent.click(screen.getByRole('button', { name: /send/i }))

    await screen.findByRole('alert')
    expect(screen.getByRole('alert')).toHaveTextContent('boom')
  })
})
