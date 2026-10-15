import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, expect, it } from 'vitest'
import { GuidesPage } from '@/pages/GuidesPage'

describe('GuidesPage', () => {
  it('renders guides heading and city filters', () => {
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    render(
      <QueryClientProvider client={client}>
        <MemoryRouter>
          <GuidesPage />
        </MemoryRouter>
      </QueryClientProvider>,
    )

    expect(screen.getByRole('heading', { name: /local guides/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /hampi/i })).toBeInTheDocument()
  })
})
