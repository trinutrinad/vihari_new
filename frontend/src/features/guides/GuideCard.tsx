import { MapPin } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Rating } from '@/components/ui/Rating'
import { cn } from '@/utils/cn'
import type { GuideSummary } from '@/types/guides'

export type GuideCardProps = {
  guide: GuideSummary
  className?: string
  onSelect?: (guide: GuideSummary) => void
}

export function GuideCard({ guide, className, onSelect }: GuideCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect?.(guide)}
      className={cn(
        'w-full overflow-hidden rounded-[1.25rem] border border-by-border bg-white text-left shadow-[var(--shadow-by-card)] transition hover:border-by-saffron/40',
        className,
      )}
    >
      <div className="h-28 bg-gradient-to-br from-by-green-dark to-by-blue" />
      <div className="space-y-2 p-3">
        <div className="flex flex-wrap gap-1.5">
          {guide.is_seed_data ? <Badge tone="neutral">Demo</Badge> : null}
          {guide.specialization ? <Badge tone="green">{guide.specialization}</Badge> : null}
        </div>
        <h3 className="font-semibold text-by-ink">{guide.display_name}</h3>
        <p className="flex items-center gap-1 text-xs text-by-muted">
          <MapPin className="size-3.5" aria-hidden />
          {guide.city_name}, {guide.state_code}
          {guide.distance_km != null ? ` · ${guide.distance_km} km` : ''}
        </p>
        <p className="text-xs text-by-muted">{guide.languages}</p>
        <div className="flex items-center justify-between gap-2">
          <Rating value={Number(guide.rating_avg)} />
          <span className="text-sm font-medium text-by-ink">
            ₹{guide.price_per_day_inr.toLocaleString('en-IN')}/day
          </span>
        </div>
      </div>
    </button>
  )
}
