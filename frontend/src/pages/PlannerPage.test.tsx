import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, expect, it } from 'vitest'
import { PlannerPage } from '@/pages/PlannerPage'

describe('PlannerPage', () => {
  it('renders planner form', () => {
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    render(
      <QueryClientProvider client={client}>
        <MemoryRouter>
          <PlannerPage />
        </MemoryRouter>
      </QueryClientProvider>,
    )

    expect(screen.getByRole('heading', { name: /ai trip planner/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /preview plan/i })).toBeInTheDocument()
  })
})
