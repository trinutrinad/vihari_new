import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, expect, it } from 'vitest'
import { TransportPage } from '@/pages/TransportPage'

describe('TransportPage', () => {
  it('renders transport heading and type filters', () => {
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    render(
      <QueryClientProvider client={client}>
        <MemoryRouter>
          <TransportPage />
        </MemoryRouter>
      </QueryClientProvider>,
    )

    expect(screen.getByRole('heading', { name: /^transport$/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /^taxi$/i })).toBeInTheDocument()
  })
})
