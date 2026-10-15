import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/services/rag', () => ({
  listRagDocuments: vi.fn(async () => ({ data: [] })),
  queryRag: vi.fn(),
  seedRagDemo: vi.fn(),
}))

import { AskPage } from '@/pages/AskPage'

describe('AskPage', () => {
  it('renders RAG ask heading and action', () => {
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    render(
      <QueryClientProvider client={client}>
        <MemoryRouter>
          <AskPage />
        </MemoryRouter>
      </QueryClientProvider>,
    )

    expect(screen.getByRole('heading', { name: /ask \(rag\)/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /ask with sources/i })).toBeInTheDocument()
  })
})
