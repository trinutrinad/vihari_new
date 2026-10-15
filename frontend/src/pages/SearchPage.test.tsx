import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, expect, it } from 'vitest'
import { SearchPage } from '@/pages/SearchPage'

describe('SearchPage', () => {
  it('renders search heading and filters', () => {
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    render(
      <QueryClientProvider client={client}>
        <MemoryRouter initialEntries={['/search']}>
          <SearchPage />
        </MemoryRouter>
      </QueryClientProvider>,
    )

    expect(screen.getByRole('heading', { name: /^search$/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /filters/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /places/i })).toBeInTheDocument()
  })
})
