import { MapPin } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Rating } from '@/components/ui/Rating'
import { cn } from '@/utils/cn'
import type { ActivitySummary } from '@/types/activities'

export type ActivityCardProps = {
  activity: ActivitySummary
  className?: string
  onSelect?: (activity: ActivitySummary) => void
}

export function ActivityCard({ activity, className, onSelect }: ActivityCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect?.(activity)}
      className={cn(
        'w-full overflow-hidden rounded-[1.25rem] border border-by-border bg-white text-left shadow-[var(--shadow-by-card)] transition hover:border-by-saffron/40',
        className,
      )}
    >
      <div className="h-28 bg-gradient-to-br from-by-saffron to-by-blue" />
      <div className="space-y-2 p-3">
        <div className="flex flex-wrap gap-1.5">
          {activity.is_seed_data ? <Badge tone="neutral">Demo</Badge> : null}
          <Badge tone="saffron">{activity.category}</Badge>
        </div>
        <h3 className="font-semibold text-by-ink">{activity.name}</h3>
        <p className="flex items-center gap-1 text-xs text-by-muted">
          <MapPin className="size-3.5" aria-hidden />
          {activity.city_name}, {activity.state_code}
          {activity.distance_km != null ? ` · ${activity.distance_km} km` : ''}
        </p>
        <div className="flex items-center justify-between gap-2">
          <Rating value={Number(activity.rating_avg)} />
          <span className="text-sm font-medium text-by-ink">
            ₹{activity.price_inr.toLocaleString('en-IN')}
          </span>
        </div>
      </div>
    </button>
  )
}
