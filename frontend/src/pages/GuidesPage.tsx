import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { SearchBar } from '@/components/ui/SearchBar'
import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States'
import { GuideCard } from '@/features/guides/GuideCard'
import { listGuides } from '@/services/guides'

const CITY_PRESETS = [
  { id: 'all', label: 'All', value: undefined },
  { id: 'hampi', label: 'Hampi', value: 'hampi' },
  { id: 'jaipur', label: 'Jaipur', value: 'jaipur' },
  { id: 'varanasi', label: 'Varanasi', value: 'varanasi' },
  { id: 'kochi', label: 'Kochi', value: 'kochi' },
] as const

export function GuidesPage() {
  const navigate = useNavigate()
  const [params, setParams] = useSearchParams()
  const [query, setQuery] = useState(params.get('q') ?? '')
  const city = params.get('city') ?? undefined
  const language = params.get('language') ?? undefined

  const guidesQuery = useQuery({
    queryKey: ['guides', { q: query, city, language }],
    queryFn: async () => {
      const response = await listGuides({
        page: 1,
        page_size: 24,
        q: query || undefined,
        city,
        language,
      })
      if (!response.data) throw new Error('Failed to load guides')
      return response.data
    },
  })

  function setCity(next?: string) {
    const updated = new URLSearchParams(params)
    if (next) updated.set('city', next)
    else updated.delete('city')
    setParams(updated)
  }

  return (
    <div className="flex flex-col gap-5 text-left">
      <div>
        <h2 className="font-display text-2xl font-semibold text-by-ink">Local guides</h2>
        <p className="mt-1 text-sm text-by-muted">
          Browse demo guide profiles. Live booking arrives in a later phase.
        </p>
        <div className="mt-4">
          <SearchBar
            defaultValue={query}
            placeholder="Search guides or specialization…"
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

      {(city || language) && (
        <div className="flex flex-wrap gap-2">
          {city ? <Badge tone="green">{city}</Badge> : null}
          {language ? <Badge tone="blue">{language}</Badge> : null}
        </div>
      )}

      {guidesQuery.isLoading ? <LoadingState label="Loading guides…" /> : null}
      {guidesQuery.isError ? (
        <ErrorState
          title="Could not load guides"
          description="Start the API and seed data, then retry."
          actionLabel="Retry"
          onAction={() => void guidesQuery.refetch()}
        />
      ) : null}

      {guidesQuery.data && guidesQuery.data.items.length === 0 ? (
        <Card>
          <EmptyState
            title="No guides found"
            description="Try another city or clear filters."
            actionLabel="Clear filters"
            onAction={() => {
              setQuery('')
              setParams(new URLSearchParams())
            }}
          />
        </Card>
      ) : null}

      {guidesQuery.data && guidesQuery.data.items.length > 0 ? (
        <>
          <p className="text-xs text-by-muted">
            Showing {guidesQuery.data.items.length} of {guidesQuery.data.meta.total}
          </p>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {guidesQuery.data.items.map((guide) => (
              <GuideCard
                key={guide.id}
                guide={guide}
                onSelect={() => navigate(`/guides/${guide.id}`)}
              />
            ))}
          </div>
        </>
      ) : null}
    </div>
  )
}
