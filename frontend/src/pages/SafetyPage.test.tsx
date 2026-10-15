import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, expect, it } from 'vitest'
import { SafetyPage } from '@/pages/SafetyPage'

describe('SafetyPage', () => {
  it('renders safety heading and city filters', () => {
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    render(
      <QueryClientProvider client={client}>
        <MemoryRouter>
          <SafetyPage />
        </MemoryRouter>
      </QueryClientProvider>,
    )

    expect(screen.getByRole('heading', { name: /^safety$/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /jaipur/i })).toBeInTheDocument()
    expect(screen.getByText(/dial 112/i)).toBeInTheDocument()
  })
})
