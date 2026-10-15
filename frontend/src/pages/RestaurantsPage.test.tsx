import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, expect, it } from 'vitest'
import { RestaurantsPage } from '@/pages/RestaurantsPage'

describe('RestaurantsPage', () => {
  it('renders restaurants heading and filters', () => {
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    render(
      <QueryClientProvider client={client}>
        <MemoryRouter>
          <RestaurantsPage />
        </MemoryRouter>
      </QueryClientProvider>,
    )

    expect(screen.getByRole('heading', { name: /^restaurants$/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /hyderabad/i })).toBeInTheDocument()
  })
})
