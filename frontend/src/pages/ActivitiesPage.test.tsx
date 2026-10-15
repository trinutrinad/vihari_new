import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, expect, it } from 'vitest'
import { ActivitiesPage } from '@/pages/ActivitiesPage'

describe('ActivitiesPage', () => {
  it('renders activities heading and filters', () => {
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    render(
      <QueryClientProvider client={client}>
        <MemoryRouter>
          <ActivitiesPage />
        </MemoryRouter>
      </QueryClientProvider>,
    )

    expect(screen.getByRole('heading', { name: /^activities$/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /rishikesh/i })).toBeInTheDocument()
  })
})
