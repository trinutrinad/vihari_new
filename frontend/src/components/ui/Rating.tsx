import { Star } from 'lucide-react'
import { cn } from '@/utils/cn'

export type RatingProps = {
  value: number
  max?: number
  className?: string
  showValue?: boolean
}

export function Rating({
  value,
  max = 5,
  className,
  showValue = true,
}: RatingProps) {
  const clamped = Math.max(0, Math.min(value, max))

  return (
    <div className={cn('inline-flex items-center gap-1 text-sm', className)}>
      <Star className="size-4 fill-by-saffron text-by-saffron" aria-hidden />
      {showValue ? (
        <span className="font-medium text-by-ink">
          {clamped.toFixed(1)}
          <span className="sr-only"> out of {max}</span>
        </span>
      ) : null}
    </div>
  )
}
