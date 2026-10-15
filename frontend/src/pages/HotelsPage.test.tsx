import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, expect, it } from 'vitest'
import { HotelsPage } from '@/pages/HotelsPage'

describe('HotelsPage', () => {
  it('renders hotels heading and filters', () => {
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    render(
      <QueryClientProvider client={client}>
        <MemoryRouter>
          <HotelsPage />
        </MemoryRouter>
      </QueryClientProvider>,
    )

    expect(screen.getByRole('heading', { name: /^hotels$/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /hyderabad/i })).toBeInTheDocument()
  })
})
