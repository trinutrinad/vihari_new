import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { SearchBar } from '@/components/ui/SearchBar'
import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States'
import { ActivityCard } from '@/features/activities/ActivityCard'
import { listActivities } from '@/services/activities'

const CITY_PRESETS = [
  { id: 'all', label: 'All', value: undefined },
  { id: 'rishikesh', label: 'Rishikesh', value: 'rishikesh' },
  { id: 'manali', label: 'Manali', value: 'manali' },
  { id: 'panaji', label: 'Panaji', value: 'panaji' },
  { id: 'jaipur', label: 'Jaipur', value: 'jaipur' },
] as const

const CATEGORY_PRESETS = [
  { id: 'adventure', label: 'Adventure', value: 'adventure' },
  { id: 'trekking', label: 'Trekking', value: 'trekking' },
  { id: 'boating', label: 'Boating', value: 'boating' },
  { id: 'photography', label: 'Photography', value: 'photography' },
] as const

export function ActivitiesPage() {
  const navigate = useNavigate()
  const [params, setParams] = useSearchParams()
  const [query, setQuery] = useState(params.get('q') ?? '')
  const city = params.get('city') ?? undefined
  const category = params.get('category') ?? undefined

  const activitiesQuery = useQuery({
    queryKey: ['activities', { q: query, city, category }],
    queryFn: async () => {
      const response = await listActivities({
        page: 1,
        page_size: 24,
        q: query || undefined,
        city,
        category,
      })
      if (!response.data) throw new Error('Failed to load activities')
      return response.data
    },
  })

  function setCity(next?: string) {
    const updated = new URLSearchParams(params)
    if (next) updated.set('city', next)
    else updated.delete('city')
    setParams(updated)
  }

  function setCategory(next?: string) {
    const updated = new URLSearchParams(params)
    if (next && updated.get('category') === next) updated.delete('category')
    else if (next) updated.set('category', next)
    else updated.delete('category')
    setParams(updated)
  }

  return (
    <div className="flex flex-col gap-5 text-left">
      <div>
        <h2 className="font-display text-2xl font-semibold text-by-ink">Activities</h2>
        <p className="mt-1 text-sm text-by-muted">
          Discover demo experiences. Booking arrives in a later phase.
        </p>
        <div className="mt-4">
          <SearchBar
            defaultValue={query}
            placeholder="Search rafting, treks, sails…"
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
        {CATEGORY_PRESETS.map((item) => (
          <Button
            key={item.id}
            size="sm"
            variant={category === item.value ? 'saffron' : 'ghost'}
            onClick={() => setCategory(item.value)}
          >
            {item.label}
          </Button>
        ))}
      </div>

      {(city || category) && (
        <div className="flex flex-wrap gap-2">
          {city ? <Badge tone="green">{city}</Badge> : null}
          {category ? <Badge tone="saffron">{category}</Badge> : null}
        </div>
      )}

      {activitiesQuery.isLoading ? <LoadingState label="Loading activities…" /> : null}
      {activitiesQuery.isError ? (
        <ErrorState
          title="Could not load activities"
          description="Start the API and seed data, then retry."
          actionLabel="Retry"
          onAction={() => void activitiesQuery.refetch()}
        />
      ) : null}

      {activitiesQuery.data && activitiesQuery.data.items.length === 0 ? (
        <Card>
          <EmptyState
            title="No activities found"
            description="Try another city or clear filters."
            actionLabel="Clear filters"
            onAction={() => {
              setQuery('')
              setParams(new URLSearchParams())
            }}
          />
        </Card>
      ) : null}

      {activitiesQuery.data && activitiesQuery.data.items.length > 0 ? (
        <>
          <p className="text-xs text-by-muted">
            Showing {activitiesQuery.data.items.length} of {activitiesQuery.data.meta.total}
          </p>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {activitiesQuery.data.items.map((activity) => (
              <ActivityCard
                key={activity.id}
                activity={activity}
                onSelect={() => navigate(`/activities/${activity.id}`)}
              />
            ))}
          </div>
        </>
      ) : null}
    </div>
  )
}
