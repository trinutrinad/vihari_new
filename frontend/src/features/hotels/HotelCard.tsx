import { MapPin, Wifi } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Rating } from '@/components/ui/Rating'
import { cn } from '@/utils/cn'
import type { HotelSummary } from '@/types/hotels'

export type HotelCardProps = {
  hotel: HotelSummary
  className?: string
  onSelect?: (hotel: HotelSummary) => void
}

export function HotelCard({ hotel, className, onSelect }: HotelCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect?.(hotel)}
      className={cn(
        'w-full overflow-hidden rounded-[1.25rem] border border-by-border bg-white text-left shadow-[var(--shadow-by-card)] transition hover:border-by-green/40',
        className,
      )}
    >
      <div className="h-28 bg-gradient-to-br from-by-blue to-by-green-dark" />
      <div className="space-y-2 p-3">
        <div className="flex flex-wrap gap-1.5">
          {hotel.is_seed_data ? <Badge tone="neutral">Demo</Badge> : null}
          {hotel.has_wifi ? (
            <Badge tone="green">
              <Wifi className="mr-1 inline size-3" aria-hidden />
              Wi‑Fi
            </Badge>
          ) : null}
          {hotel.has_breakfast ? <Badge tone="saffron">Breakfast</Badge> : null}
        </div>
        <h3 className="font-semibold text-by-ink">{hotel.name}</h3>
        <p className="flex items-center gap-1 text-xs text-by-muted">
          <MapPin className="size-3.5" aria-hidden />
          {hotel.city_name}, {hotel.state_code}
          {hotel.distance_km != null ? ` · ${hotel.distance_km} km` : ''}
        </p>
        <div className="flex items-center justify-between gap-2">
          <Rating value={Number(hotel.rating_avg)} />
          <span className="text-sm font-medium text-by-ink">
            {hotel.starting_price_inr != null
              ? `from ₹${hotel.starting_price_inr.toLocaleString('en-IN')}`
              : 'Price TBD'}
          </span>
        </div>
      </div>
    </button>
  )
}
