import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { SearchBar } from '@/components/ui/SearchBar'
import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States'
import { TransportCard } from '@/features/transport/TransportCard'
import { listTransportOptions } from '@/services/transport'

const TYPE_PRESETS = [
  { id: 'all', label: 'All', value: undefined },
  { id: 'auto', label: 'Auto', value: 'auto' },
  { id: 'taxi', label: 'Taxi', value: 'taxi' },
  { id: 'bike', label: 'Bike', value: 'bike' },
  { id: 'bus', label: 'Bus', value: 'bus' },
  { id: 'train', label: 'Train', value: 'train' },
  { id: 'airport_transfer', label: 'Airport', value: 'airport_transfer' },
  { id: 'outstation_cab', label: 'Outstation', value: 'outstation_cab' },
] as const

export function TransportPage() {
  const navigate = useNavigate()
  const [params, setParams] = useSearchParams()
  const [query, setQuery] = useState(params.get('q') ?? '')
  const vehicleType = params.get('type') ?? undefined

  const transportQuery = useQuery({
    queryKey: ['transport', { q: query, vehicleType }],
    queryFn: async () => {
      const response = await listTransportOptions({
        page: 1,
        page_size: 24,
        q: query || undefined,
        vehicle_type: vehicleType,
      })
      if (!response.data) throw new Error('Failed to load transport options')
      return response.data
    },
  })

  function setType(next?: string) {
    const updated = new URLSearchParams(params)
    if (next) updated.set('type', next)
    else updated.delete('type')
    setParams(updated)
  }

  return (
    <div className="flex flex-col gap-5 text-left">
      <div>
        <h2 className="font-display text-2xl font-semibold text-by-ink">Transport</h2>
        <p className="mt-1 text-sm text-by-muted">
          Compare demo fare options. Live ride booking arrives in a later phase.
        </p>
        <div className="mt-4">
          <SearchBar
            defaultValue={query}
            placeholder="Search autos, taxis, buses…"
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
        {TYPE_PRESETS.map((item) => (
          <Button
            key={item.id}
            size="sm"
            variant={vehicleType === item.value ? 'primary' : 'ghost'}
            onClick={() => setType(item.value)}
          >
            {item.label}
          </Button>
        ))}
      </div>

      {vehicleType ? (
        <div className="flex flex-wrap gap-2">
          <Badge tone="blue">{vehicleType.replaceAll('_', ' ')}</Badge>
        </div>
      ) : null}

      {transportQuery.isLoading ? <LoadingState label="Loading transport…" /> : null}
      {transportQuery.isError ? (
        <ErrorState
          title="Could not load transport"
          description="Start the API and seed data, then retry."
          actionLabel="Retry"
          onAction={() => void transportQuery.refetch()}
        />
      ) : null}

      {transportQuery.data && transportQuery.data.items.length === 0 ? (
        <Card>
          <EmptyState
            title="No options found"
            description="Try another vehicle type or clear filters."
            actionLabel="Clear filters"
            onAction={() => {
              setQuery('')
              setParams(new URLSearchParams())
            }}
          />
        </Card>
      ) : null}

      {transportQuery.data && transportQuery.data.items.length > 0 ? (
        <>
          <p className="text-xs text-by-muted">
            Showing {transportQuery.data.items.length} of {transportQuery.data.meta.total}
          </p>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {transportQuery.data.items.map((option) => (
              <TransportCard
                key={option.id}
                option={option}
                onSelect={() => navigate(`/transport/${option.id}`)}
              />
            ))}
          </div>
        </>
      ) : null}
    </div>
  )
}
