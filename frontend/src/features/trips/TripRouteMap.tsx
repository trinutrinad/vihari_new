import { MapCanvas } from '@/features/maps/MapCanvas'
import type { MapLatLng, MapMarkerModel } from '@/features/maps/mapProvider'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import type { TripMapPoint } from '@/types/trips'

const TONES: Array<NonNullable<MapMarkerModel['tone']>> = ['green', 'saffron', 'blue']

export type TripRouteMapProps = {
  points: TripMapPoint[]
  title?: string
  emptyHint?: string
  className?: string
}

export function TripRouteMap({
  points,
  title = 'Trip route',
  emptyHint = 'Add places with coordinates to see the route on the map.',
  className,
}: TripRouteMapProps) {
  const route: MapLatLng[] = points.map((point) => ({
    lat: Number(point.latitude),
    lng: Number(point.longitude),
  }))

  const markers: MapMarkerModel[] = points.map((point, index) => ({
    id: point.id,
    position: { lat: Number(point.latitude), lng: Number(point.longitude) },
    title: point.label,
    subtitle: `Day ${point.day_number}`,
    href: point.href ?? undefined,
    tone: TONES[index % TONES.length],
  }))

  if (points.length === 0) {
    return (
      <Card className="space-y-2 text-left">
        <h3 className="text-lg font-semibold text-by-ink">{title}</h3>
        <p className="text-sm text-by-muted">{emptyHint}</p>
      </Card>
    )
  }

  return (
    <Card className="space-y-3 text-left">
      <div className="flex flex-wrap items-center gap-2">
        <h3 className="text-lg font-semibold text-by-ink">{title}</h3>
        <Badge tone="green">{points.length} stops</Badge>
      </div>
      <MapCanvas
        center={route[0]}
        zoom={points.length === 1 ? 12 : 6}
        fitMarkers
        route={route.length >= 2 ? route : undefined}
        markers={markers}
        className={className ?? 'h-56'}
      />
    </Card>
  )
}
