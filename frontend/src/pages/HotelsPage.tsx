import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { SearchBar } from '@/components/ui/SearchBar'
import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States'
import { HotelCard } from '@/features/hotels/HotelCard'
import { listHotels } from '@/services/hotels'

const CITY_PRESETS = [
  { id: 'all', label: 'All', value: undefined },
  { id: 'hyderabad', label: 'Hyderabad', value: 'hyderabad' },
  { id: 'jaipur', label: 'Jaipur', value: 'jaipur' },
  { id: 'panaji', label: 'Goa', value: 'panaji' },
  { id: 'manali', label: 'Manali', value: 'manali' },
  { id: 'kochi', label: 'Kochi', value: 'kochi' },
] as const

export function HotelsPage() {
  const navigate = useNavigate()
  const [params, setParams] = useSearchParams()
  const [query, setQuery] = useState(params.get('q') ?? '')
  const city = params.get('city') ?? undefined
  const wifi = params.get('wifi') === '1'
  const breakfast = params.get('breakfast') === '1'
  const [maxPrice, setMaxPrice] = useState(params.get('max_price') ?? '')

  const hotelsQuery = useQuery({
    queryKey: ['hotels', { q: query, city, wifi, breakfast, maxPrice }],
    queryFn: async () => {
      const response = await listHotels({
        page: 1,
        page_size: 24,
        q: query || undefined,
        city,
        wifi: wifi || undefined,
        breakfast: breakfast || undefined,
        max_price: maxPrice ? Number(maxPrice) : undefined,
      })
      if (!response.data) throw new Error('Failed to load hotels')
      return response.data
    },
  })

  function setCity(next?: string) {
    const updated = new URLSearchParams(params)
    if (next) updated.set('city', next)
    else updated.delete('city')
    setParams(updated)
  }

  function toggleFlag(key: 'wifi' | 'breakfast') {
    const updated = new URLSearchParams(params)
    if (updated.get(key) === '1') updated.delete(key)
    else updated.set(key, '1')
    setParams(updated)
  }

  function applyMaxPrice() {
    const updated = new URLSearchParams(params)
    if (maxPrice) updated.set('max_price', maxPrice)
    else updated.delete('max_price')
    setParams(updated)
  }

  return (
    <div className="flex flex-col gap-5 text-left">
      <div>
        <h2 className="font-display text-2xl font-semibold text-by-ink">Hotels</h2>
        <p className="mt-1 text-sm text-by-muted">
          Browse demo stays. Booking checkout arrives in a later phase.
        </p>
        <div className="mt-4">
          <SearchBar
            defaultValue={query}
            placeholder="Search hotels…"
            onSubmitSearch={(value) => {
              setQuery(value.trim())
              const updated = new URLSearchParams(params)
              if (value.trim()) updated.set('q', value.trim())
              else updated.delete('q')
              setParams(updated)
            }}
          />
        </div>
      </div>

      <div className="scrollbar-hide -mx-4 flex gap-2 overflow-x-auto px-4">
        {CITY_PRESETS.map((item) => (
          <Button
            key={item.id}
            size="sm"
            variant={city === item.value ? 'primary' : 'ghost'}
            onClick={() => setCity(item.value)}
          >
            {item.label}
          </Button>
        ))}
      </div>

      <div className="flex flex-wrap items-end gap-2">
        <Button
          size="sm"
          variant={wifi ? 'saffron' : 'ghost'}
          onClick={() => toggleFlag('wifi')}
        >
          Wi‑Fi
        </Button>
        <Button
          size="sm"
          variant={breakfast ? 'saffron' : 'ghost'}
          onClick={() => toggleFlag('breakfast')}
        >
          Breakfast
        </Button>
        <Input
          label="Max ₹ / night"
          type="number"
          min={0}
          value={maxPrice}
          onChange={(event) => setMaxPrice(event.target.value)}
          className="w-36"
        />
        <Button size="sm" onClick={applyMaxPrice}>
          Apply
        </Button>
      </div>

      {(city || wifi || breakfast || params.get('max_price')) && (
        <div className="flex flex-wrap gap-2">
          {city ? <Badge tone="green">{city}</Badge> : null}
          {wifi ? <Badge tone="saffron">Wi‑Fi</Badge> : null}
          {breakfast ? <Badge tone="saffron">Breakfast</Badge> : null}
          {params.get('max_price') ? (
            <Badge tone="blue">Max ₹{params.get('max_price')}</Badge>
          ) : null}
        </div>
      )}

      {hotelsQuery.isLoading ? <LoadingState label="Loading hotels…" /> : null}
      {hotelsQuery.isError ? (
        <ErrorState
          title="Could not load hotels"
          description="Start the API and seed data, then retry."
          actionLabel="Retry"
          onAction={() => void hotelsQuery.refetch()}
        />
      ) : null}

      {hotelsQuery.data && hotelsQuery.data.items.length === 0 ? (
        <Card>
          <EmptyState
            title="No hotels found"
            description="Try another city or clear filters."
            actionLabel="Clear filters"
            onAction={() => {
              setQuery('')
              setMaxPrice('')
              setParams(new URLSearchParams())
            }}
          />
        </Card>
      ) : null}

      {hotelsQuery.data && hotelsQuery.data.items.length > 0 ? (
        <>
          <p className="text-xs text-by-muted">
            Showing {hotelsQuery.data.items.length} of {hotelsQuery.data.meta.total}
          </p>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {hotelsQuery.data.items.map((hotel) => (
              <HotelCard
                key={hotel.id}
                hotel={hotel}
                onSelect={() => navigate(`/hotels/${hotel.id}`)}
              />
            ))}
          </div>
        </>
      ) : null}
    </div>
  )
}
