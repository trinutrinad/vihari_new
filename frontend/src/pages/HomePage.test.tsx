import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { ReactElement } from 'react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, expect, it, vi } from 'vitest'
import { HomePage } from '@/pages/HomePage'
import { PlaceCard } from '@/components/ui/PlaceCard'
import { HOME_PLACES } from '@/constants/home'
import { homePlaceToCard } from '@/utils/placeCards'

function renderWithProviders(ui: ReactElement) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('HomePage', () => {
  it('renders hero, search, and AI planner', () => {
    renderWithProviders(<HomePage />)

    expect(
      screen.getByRole('heading', { name: /where do you want to go/i }),
    ).toBeInTheDocument()
    expect(
      screen.getByPlaceholderText(/search places, temples, hotels, food/i),
    ).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /categories/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /ai trip planner/i })).toBeInTheDocument()
  }, 10_000)
})

describe('PlaceCard', () => {
  it('shows place details and handles select', async () => {
    const user = userEvent.setup()
    const onSelect = vi.fn()
    const place = homePlaceToCard(HOME_PLACES[0])

    render(<PlaceCard place={place} onSelect={onSelect} />)

    expect(screen.getByText(place.name)).toBeInTheDocument()
    expect(screen.getByText(/^demo$/i)).toBeInTheDocument()
    await user.click(screen.getByRole('button'))
    expect(onSelect).toHaveBeenCalledWith(place)
  })
})
