import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { PlaceCard } from '@/components/ui/PlaceCard'
import { SearchBar } from '@/components/ui/SearchBar'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { LoadingState, ErrorState, EmptyState } from '@/components/feedback/States'
import { listPlaceCategories, listPlaces } from '@/services/places'
import { apiPlaceToCard } from '@/utils/placeCards'

export function ExplorePage() {
  const navigate = useNavigate()
  const [params, setParams] = useSearchParams()
  const [query, setQuery] = useState(params.get('q') ?? '')
  const category = params.get('category') ?? undefined
  const featured = params.get('featured') === 'true' ? true : undefined

  const categoriesQuery = useQuery({
    queryKey: ['place-categories'],
    queryFn: async () => {
      const response = await listPlaceCategories()
      return response.data ?? []
    },
  })

  const placesQuery = useQuery({
    queryKey: ['places', { q: query, category, featured }],
    queryFn: async () => {
      const response = await listPlaces({
        page: 1,
        page_size: 24,
        q: query || undefined,
        category,
        featured,
      })
      if (!response.data) throw new Error('Failed to load places')
      return response.data
    },
  })

  const activeCategoryName = useMemo(() => {
    return categoriesQuery.data?.find((item) => item.slug === category)?.name
  }, [categoriesQuery.data, category])

  function updateCategory(next?: string) {
    const updated = new URLSearchParams(params)
    if (next) updated.set('category', next)
    else updated.delete('category')
    setParams(updated)
  }

  return (
    <div className="flex flex-col gap-5 text-left">
      <div>
        <h2 className="font-display text-2xl font-semibold text-by-ink">Explore</h2>
        <p className="mt-1 text-sm text-by-muted">
          Browse seeded Indian destinations. Open the map for pins nearby.
        </p>
        <div className="mt-3">
          <Button size="sm" variant="secondary" onClick={() => navigate('/map')}>
            View on map
          </Button>
        </div>
        <div className="mt-4">
          <SearchBar
            defaultValue={query}
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
        <Button
          size="sm"
          variant={!category ? 'primary' : 'ghost'}
          onClick={() => updateCategory(undefined)}
        >
          All
        </Button>
        {(categoriesQuery.data ?? []).map((item) => (
          <Button
            key={item.id}
            size="sm"
            variant={category === item.slug ? 'primary' : 'ghost'}
            onClick={() => updateCategory(item.slug)}
          >
            {item.name}
          </Button>
        ))}
      </div>

      {(activeCategoryName || featured) && (
        <div className="flex flex-wrap gap-2">
          {activeCategoryName ? <Badge tone="green">{activeCategoryName}</Badge> : null}
          {featured ? <Badge tone="saffron">Featured</Badge> : null}
        </div>
      )}

      {placesQuery.isLoading ? <LoadingState label="Loading places…" /> : null}
      {placesQuery.isError ? (
        <ErrorState
          title="Could not load places"
          description="Start the API and seed data, then retry."
          actionLabel="Retry"
          onAction={() => void placesQuery.refetch()}
        />
      ) : null}

      {placesQuery.data && placesQuery.data.items.length === 0 ? (
        <Card>
          <EmptyState
            title="No places found"
            description="Try another category or clear search."
            actionLabel="Clear filters"
            onAction={() => {
              setQuery('')
              setParams(new URLSearchParams())
            }}
          />
        </Card>
      ) : null}

      {placesQuery.data && placesQuery.data.items.length > 0 ? (
        <>
          <p className="text-xs text-by-muted">
            Showing {placesQuery.data.items.length} of {placesQuery.data.meta.total}
          </p>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {placesQuery.data.items.map((place) => (
              <PlaceCard
                key={place.id}
                className="w-full"
                place={apiPlaceToCard(place)}
                onSelect={() => navigate(`/places/${place.id}`)}
              />
            ))}
          </div>
        </>
      ) : null}
    </div>
  )
}
