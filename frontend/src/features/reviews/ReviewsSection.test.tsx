import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, expect, it } from 'vitest'
import { ReviewsSection } from '@/features/reviews/ReviewsSection'

describe('ReviewsSection', () => {
  it('renders reviews heading and sign-in CTA when logged out', () => {
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    render(
      <QueryClientProvider client={client}>
        <MemoryRouter>
          <ReviewsSection targetType="place" targetId="00000000-0000-0000-0000-000000000001" />
        </MemoryRouter>
      </QueryClientProvider>,
    )

    expect(screen.getByRole('heading', { name: /^reviews$/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in to review/i })).toBeInTheDocument()
  })
})
