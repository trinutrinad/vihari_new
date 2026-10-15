import { Badge } from '@/components/ui/Badge'
import { cn } from '@/utils/cn'
import type { TransportOptionSummary } from '@/types/transport'

export type TransportCardProps = {
  option: TransportOptionSummary
  className?: string
  onSelect?: (option: TransportOptionSummary) => void
}

function formatType(value: string) {
  return value.replaceAll('_', ' ')
}

export function TransportCard({ option, className, onSelect }: TransportCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect?.(option)}
      className={cn(
        'w-full overflow-hidden rounded-[1.25rem] border border-by-border bg-white text-left shadow-[var(--shadow-by-card)] transition hover:border-by-saffron/40',
        className,
      )}
    >
      <div className="h-24 bg-gradient-to-br from-by-blue to-by-green-dark" />
      <div className="space-y-2 p-3">
        <div className="flex flex-wrap gap-1.5">
          {option.is_seed_data ? <Badge tone="neutral">Demo</Badge> : null}
          <Badge tone="blue">{formatType(option.vehicle_type)}</Badge>
        </div>
        <h3 className="font-semibold text-by-ink">{option.name}</h3>
        <p className="text-xs text-by-muted">
          Base ₹{option.base_fare_inr.toLocaleString('en-IN')}
          {option.per_km_inr > 0
            ? ` · ₹${option.per_km_inr.toLocaleString('en-IN')}/km`
            : ' · variable fare'}
        </p>
        {option.sample_fare_10km_inr != null ? (
          <p className="text-sm font-medium text-by-ink">
            ~₹{option.sample_fare_10km_inr.toLocaleString('en-IN')} for 10 km
          </p>
        ) : (
          <p className="text-sm text-by-muted">Fare varies by route</p>
        )}
      </div>
    </button>
  )
}
