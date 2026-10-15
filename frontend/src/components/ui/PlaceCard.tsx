import { MapPin } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Rating } from '@/components/ui/Rating'
import { cn } from '@/utils/cn'

export type PlaceCardModel = {
  id: string
  name: string
  locationLabel: string
  categoryLabel: string
  rating: number
  distanceKm?: number | null
  estimatedCostInr?: number | null
  coverClassName?: string
  imageUrl?: string | null
  isDemo?: boolean
}

export type PlaceCardProps = {
  place: PlaceCardModel
  className?: string
  onSelect?: (place: PlaceCardModel) => void
}

export function PlaceCard({ place, className, onSelect }: PlaceCardProps) {
  const hasImage = Boolean(place.imageUrl)
  const cover = place.coverClassName ?? 'from-[#1b7a4e] to-[#0b3d91]'

  return (
    <button
      type="button"
      onClick={() => onSelect?.(place)}
      className={cn(
        'group w-[17.5rem] shrink-0 overflow-hidden rounded-[var(--radius-by)] border border-by-border/70 bg-by-surface text-left shadow-[var(--shadow-by-card)] transition duration-300',
        'hover:-translate-y-0.5 hover:shadow-lg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-by-green',
        className,
      )}
    >
      <div
        className={cn(
          'relative aspect-[4/3] overflow-hidden',
          hasImage ? 'bg-by-green-soft' : `bg-gradient-to-br ${cover}`,
        )}
      >
        {hasImage ? (
          <img
            src={place.imageUrl ?? undefined}
            alt=""
            loading="lazy"
            className="size-full object-cover transition duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(255,255,255,0.28),transparent_45%)]" />
        )}
        <div className="absolute left-2 top-2">
          <Badge tone="green">{place.categoryLabel}</Badge>
        </div>
        {place.isDemo ? (
          <div className="absolute bottom-2 right-2">
            <Badge tone="neutral">Demo</Badge>
          </div>
        ) : null}
        {!hasImage ? (
          <p className="absolute bottom-3 left-3 max-w-[85%] font-display text-lg font-semibold text-white drop-shadow">
            {place.locationLabel.split(',')[0]}
          </p>
        ) : null}
      </div>
      <div className="space-y-2 p-3">
        <h4 className="line-clamp-2 text-sm font-semibold text-by-ink">{place.name}</h4>
        <p className="flex items-center gap-1 text-xs text-by-muted">
          <MapPin className="size-3.5 shrink-0" aria-hidden />
          <span className="truncate">{place.locationLabel}</span>
        </p>
        <div className="flex items-center justify-between gap-2">
          <Rating value={place.rating} />
          {place.distanceKm != null ? (
            <span className="text-xs text-by-muted">{place.distanceKm.toFixed(1)} km</span>
          ) : null}
        </div>
        {place.estimatedCostInr != null ? (
          <p className="text-sm font-medium text-by-green">
            ~₹{place.estimatedCostInr.toLocaleString('en-IN')}
            <span className="font-normal text-by-muted"> est.</span>
          </p>
        ) : null}
      </div>
    </button>
  )
}
