import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { SearchBar } from '@/components/ui/SearchBar'
import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States'
import { RestaurantCard } from '@/features/restaurants/RestaurantCard'
import { listRestaurants } from '@/services/restaurants'

const CITY_PRESETS = [
  { id: 'all', label: 'All', value: undefined },
  { id: 'hyderabad', label: 'Hyderabad', value: 'hyderabad' },
  { id: 'jaipur', label: 'Jaipur', value: 'jaipur' },
  { id: 'chennai', label: 'Chennai', value: 'chennai' },
  { id: 'mumbai', label: 'Mumbai', value: 'mumbai' },
  { id: 'kolkata', label: 'Kolkata', value: 'kolkata' },
] as const

export function RestaurantsPage() {
  const navigate = useNavigate()
  const [params, setParams] = useSearchParams()
  const [query, setQuery] = useState(params.get('q') ?? '')
  const city = params.get('city') ?? undefined
  const vegetarian = params.get('veg') === '1'
  const cuisine = params.get('cuisine') ?? undefined

  const restaurantsQuery = useQuery({
    queryKey: ['restaurants', { q: query, city, vegetarian, cuisine }],
    queryFn: async () => {
      const response = await listRestaurants({
        page: 1,
        page_size: 24,
        q: query || undefined,
        city,
        vegetarian: vegetarian || undefined,
        cuisine,
      })
      if (!response.data) throw new Error('Failed to load restaurants')
      return response.data
    },
  })

  function setCity(next?: string) {
    const updated = new URLSearchParams(params)
    if (next) updated.set('city', next)
    else updated.delete('city')
    setParams(updated)
  }

  function toggleVeg() {
    const updated = new URLSearchParams(params)
    if (updated.get('veg') === '1') updated.delete('veg')
    else updated.set('veg', '1')
    setParams(updated)
  }

  return (
    <div className="flex flex-col gap-5 text-left">
      <div>
        <h2 className="font-display text-2xl font-semibold text-by-ink">Restaurants</h2>
        <p className="mt-1 text-sm text-by-muted">
          Discover demo kitchens and menus. Food ordering arrives in a later phase.
        </p>
        <div className="mt-4">
          <SearchBar
            defaultValue={query}
            placeholder="Search restaurants or cuisine…"
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

      <div className="flex flex-wrap gap-2">
        <Button size="sm" variant={vegetarian ? 'saffron' : 'ghost'} onClick={toggleVeg}>
          Vegetarian
        </Button>
      </div>

      {(city || vegetarian || cuisine) && (
        <div className="flex flex-wrap gap-2">
          {city ? <Badge tone="green">{city}</Badge> : null}
          {vegetarian ? <Badge tone="saffron">Veg</Badge> : null}
          {cuisine ? <Badge tone="blue">{cuisine}</Badge> : null}
        </div>
      )}

      {restaurantsQuery.isLoading ? <LoadingState label="Loading restaurants…" /> : null}
      {restaurantsQuery.isError ? (
        <ErrorState
          title="Could not load restaurants"
          description="Start the API and seed data, then retry."
          actionLabel="Retry"
          onAction={() => void restaurantsQuery.refetch()}
        />
      ) : null}

      {restaurantsQuery.data && restaurantsQuery.data.items.length === 0 ? (
        <Card>
          <EmptyState
            title="No restaurants found"
            description="Try another city or clear filters."
            actionLabel="Clear filters"
            onAction={() => {
              setQuery('')
              setParams(new URLSearchParams())
            }}
          />
        </Card>
      ) : null}

      {restaurantsQuery.data && restaurantsQuery.data.items.length > 0 ? (
        <>
          <p className="text-xs text-by-muted">
            Showing {restaurantsQuery.data.items.length} of {restaurantsQuery.data.meta.total}
          </p>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {restaurantsQuery.data.items.map((restaurant) => (
              <RestaurantCard
                key={restaurant.id}
                restaurant={restaurant}
                onSelect={() => navigate(`/restaurants/${restaurant.id}`)}
              />
            ))}
          </div>
        </>
      ) : null}
    </div>
  )
}
