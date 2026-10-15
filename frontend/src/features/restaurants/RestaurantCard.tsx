import { MapPin } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Rating } from '@/components/ui/Rating'
import { cn } from '@/utils/cn'
import type { RestaurantSummary } from '@/types/restaurants'

export type RestaurantCardProps = {
  restaurant: RestaurantSummary
  className?: string
  onSelect?: (restaurant: RestaurantSummary) => void
}

function priceLabel(level: number) {
  return '₹'.repeat(Math.min(Math.max(level, 1), 4))
}

export function RestaurantCard({ restaurant, className, onSelect }: RestaurantCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect?.(restaurant)}
      className={cn(
        'w-full overflow-hidden rounded-[1.25rem] border border-by-border bg-white text-left shadow-[var(--shadow-by-card)] transition hover:border-by-saffron/40',
        className,
      )}
    >
      <div className="h-28 bg-gradient-to-br from-by-saffron to-by-green-dark" />
      <div className="space-y-2 p-3">
        <div className="flex flex-wrap gap-1.5">
          {restaurant.is_seed_data ? <Badge tone="neutral">Demo</Badge> : null}
          {restaurant.is_vegetarian ? <Badge tone="green">Veg</Badge> : null}
          {restaurant.is_street_food ? <Badge tone="saffron">Street food</Badge> : null}
          {restaurant.cuisine_tags ? <Badge tone="blue">{restaurant.cuisine_tags}</Badge> : null}
        </div>
        <h3 className="font-semibold text-by-ink">{restaurant.name}</h3>
        <p className="flex items-center gap-1 text-xs text-by-muted">
          <MapPin className="size-3.5" aria-hidden />
          {restaurant.city_name}, {restaurant.state_code}
          {restaurant.distance_km != null ? ` · ${restaurant.distance_km} km` : ''}
        </p>
        <div className="flex items-center justify-between gap-2">
          <Rating value={Number(restaurant.rating_avg)} />
          <span className="text-sm font-medium text-by-ink">
            {priceLabel(restaurant.price_level)}
          </span>
        </div>
      </div>
    </button>
  )
}
