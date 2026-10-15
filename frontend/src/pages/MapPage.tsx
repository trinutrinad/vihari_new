import { useCallback, useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { MapPinned } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States'
import { MapCanvas } from '@/features/maps/MapCanvas'
import {
  DEMO_CITY_PRESETS,
  type MapBounds,
  type MapMarkerModel,
} from '@/features/maps/mapProvider'
import { fetchMapCities, fetchMapPins } from '@/services/maps'

export function MapPage() {
  const navigate = useNavigate()
  const [params, setParams] = useSearchParams()
  const cityId = params.get('city') ?? 'india'
  const preset =
    DEMO_CITY_PRESETS.find((item) => item.id === cityId) ?? DEMO_CITY_PRESETS[0]

  const [center, setCenter] = useState(preset.center)
  const [zoom, setZoom] = useState(preset.zoom)
  const [bounds, setBounds] = useState<MapBounds | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const citiesQuery = useQuery({
    queryKey: ['map-cities'],
    queryFn: async () => {
      const response = await fetchMapCities()
      return response.data ?? []
    },
  })

  const pinsQuery = useQuery({
    queryKey: ['map-pins', bounds],
    queryFn: async () => {
      if (!bounds) return null
      const response = await fetchMapPins({ ...bounds, limit: 80 })
      if (!response.data) throw new Error('Map pins unavailable')
      return response.data
    },
    enabled: Boolean(bounds),
  })

  const markers: MapMarkerModel[] = useMemo(
    () =>
      (pinsQuery.data?.pins ?? []).map((pin) => ({
        id: pin.id,
        position: { lat: Number(pin.latitude), lng: Number(pin.longitude) },
        title: pin.name,
        subtitle: `${pin.city_name}, ${pin.state_code}${pin.is_seed_data ? ' · Demo' : ''}`,
        href: pin.href,
        tone: selectedId === pin.id ? 'saffron' : 'green',
      })),
    [pinsQuery.data?.pins, selectedId],
  )

  const onBoundsChange = useCallback((next: MapBounds) => {
    setBounds((prev) => {
      if (
        prev &&
        Math.abs(prev.north - next.north) < 0.0001 &&
        Math.abs(prev.south - next.south) < 0.0001 &&
        Math.abs(prev.east - next.east) < 0.0001 &&
        Math.abs(prev.west - next.west) < 0.0001
      ) {
        return prev
      }
      return next
    })
  }, [])

  function selectPreset(id: string) {
    const next = DEMO_CITY_PRESETS.find((item) => item.id === id)
    if (!next) return
    setCenter(next.center)
    setZoom(next.zoom)
    const search = new URLSearchParams(params)
    if (id === 'india') search.delete('city')
    else search.set('city', id)
    setParams(search)
  }

  function flyToApiCity(lat: number, lng: number, slug: string) {
    setCenter({ lat, lng })
    setZoom(11)
    const search = new URLSearchParams(params)
    search.set('city', slug)
    setParams(search)
  }

  return (
    <div className="flex flex-col gap-4 text-left">
      <div>
        <h2 className="font-display text-2xl font-semibold text-by-ink">Map</h2>
        <p className="mt-1 text-sm text-by-muted">
          Explore destinations on OpenStreetMap. Pan the map to load pins in view.
        </p>
      </div>

      <div className="scrollbar-hide -mx-4 flex gap-2 overflow-x-auto px-4">
        {DEMO_CITY_PRESETS.map((item) => (
          <Button
            key={item.id}
            size="sm"
            variant={cityId === item.id || (cityId === 'india' && item.id === 'india') ? 'primary' : 'ghost'}
            onClick={() => selectPreset(item.id)}
          >
            {item.label}
          </Button>
        ))}
      </div>

      {(citiesQuery.data?.length ?? 0) > 0 ? (
        <div className="scrollbar-hide -mx-4 flex gap-2 overflow-x-auto px-4">
          {citiesQuery.data?.slice(0, 8).map((city) => (
            <button
              key={city.id}
              type="button"
              className="shrink-0 rounded-full border border-by-border bg-white px-3 py-1.5 text-sm"
              onClick={() =>
                flyToApiCity(Number(city.latitude), Number(city.longitude), city.slug)
              }
            >
              {city.name}
              <span className="ml-1 text-by-muted">({city.place_count})</span>
            </button>
          ))}
        </div>
      ) : null}

      <MapCanvas
        center={center}
        zoom={zoom}
        markers={markers}
        onBoundsChange={onBoundsChange}
        onMarkerSelect={(marker) => {
          setSelectedId(marker.id)
          if (marker.href) navigate(marker.href)
        }}
        className="h-[min(60vh,28rem)]"
      />

      {pinsQuery.isLoading ? <LoadingState label="Loading map pins…" /> : null}
      {pinsQuery.isError ? (
        <ErrorState
          title="Map data unavailable"
          description="Start the API and seed data, then pan the map again."
          actionLabel="Retry"
          onAction={() => void pinsQuery.refetch()}
        />
      ) : null}

      {pinsQuery.data ? (
        <Card className="space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="flex items-center gap-2 text-sm font-semibold text-by-ink">
              <MapPinned className="size-4" aria-hidden />
              {pinsQuery.data.total} pin{pinsQuery.data.total === 1 ? '' : 's'} in view
            </h3>
            <Badge tone="neutral">{pinsQuery.data.provider}</Badge>
          </div>
          <p className="text-xs text-by-muted">{pinsQuery.data.notice}</p>
          {pinsQuery.data.pins.length === 0 ? (
            <EmptyState
              title="No pins here"
              description="Zoom out or choose another city preset."
            />
          ) : (
            <ul className="divide-y divide-by-border">
              {pinsQuery.data.pins.slice(0, 12).map((pin) => (
                <li key={pin.id}>
                  <button
                    type="button"
                    className="flex w-full items-start justify-between gap-3 py-2.5 text-left hover:bg-by-green-soft/50"
                    onClick={() => navigate(pin.href)}
                  >
                    <span>
                      <span className="block text-sm font-medium text-by-ink">{pin.name}</span>
                      <span className="text-xs text-by-muted">
                        {pin.city_name}, {pin.state_code}
                      </span>
                    </span>
                    <Badge tone={pin.is_seed_data ? 'neutral' : 'green'}>
                      {Number(pin.rating_avg).toFixed(1)}
                    </Badge>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </Card>
      ) : null}

    </div>
  )
}
