import { Badge } from '@/components/ui/Badge'
import { Rating } from '@/components/ui/Rating'
import type { SearchResultItem } from '@/types/search'
import { cn } from '@/utils/cn'

const toneByType: Record<string, 'green' | 'saffron' | 'blue' | 'neutral'> = {
  place: 'green',
  hotel: 'blue',
  restaurant: 'saffron',
  guide: 'green',
  activity: 'saffron',
  city: 'blue',
  state: 'neutral',
}

export type SearchResultCardProps = {
  item: SearchResultItem
  onSelect?: (item: SearchResultItem) => void
  className?: string
}

export function SearchResultCard({ item, onSelect, className }: SearchResultCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect?.(item)}
      className={cn(
        'w-full rounded-[var(--radius-by)] border border-by-border/70 bg-white p-4 text-left shadow-[var(--shadow-by-card)] transition hover:-translate-y-0.5 hover:shadow-lg',
        'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-by-green',
        className,
      )}
    >
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone={toneByType[item.entity_type] ?? 'neutral'}>{item.entity_type}</Badge>
        {item.category ? <Badge tone="neutral">{item.category}</Badge> : null}
        {item.is_seed_data ? <Badge tone="neutral">Demo</Badge> : null}
      </div>
      <h3 className="mt-2 text-base font-semibold text-by-ink">{item.title}</h3>
      {item.subtitle ? <p className="mt-1 line-clamp-2 text-sm text-by-muted">{item.subtitle}</p> : null}
      <div className="mt-3 flex flex-wrap items-center gap-3 text-sm text-by-muted">
        {item.location_label ? <span>{item.location_label}</span> : null}
        {item.rating_avg != null ? <Rating value={Number(item.rating_avg)} /> : null}
        {item.distance_km != null ? <span>{item.distance_km.toFixed(1)} km</span> : null}
        {item.estimated_cost_inr != null ? (
          <span className="font-medium text-by-green">
            ~₹{item.estimated_cost_inr.toLocaleString('en-IN')}
          </span>
        ) : null}
      </div>
    </button>
  )
}
