import { Bell, MapPin } from 'lucide-react'
import { APP_NAME } from '@/constants/app'
import { cn } from '@/utils/cn'

export type TopNavigationProps = {
  title?: string
  subtitle?: string
  className?: string
  showBrand?: boolean
}

export function TopNavigation({
  title,
  subtitle,
  className,
  showBrand = true,
}: TopNavigationProps) {
  return (
    <header
      className={cn(
        'sticky top-0 z-30 border-b border-by-border/80 bg-white/90 backdrop-blur',
        className,
      )}
    >
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-3">
        <div className="min-w-0 text-left">
          {showBrand ? (
            <p className="font-display text-xl font-semibold tracking-tight text-by-green">
              {APP_NAME}
            </p>
          ) : null}
          {title ? (
            <h1 className="truncate text-base font-semibold text-by-ink">{title}</h1>
          ) : null}
          {subtitle ? (
            <p className="mt-0.5 flex items-center gap-1 truncate text-xs text-by-muted">
              <MapPin className="size-3.5 shrink-0" aria-hidden />
              {subtitle}
            </p>
          ) : null}
        </div>
        <button
          type="button"
          className="inline-flex size-10 items-center justify-center rounded-full border border-by-border bg-white text-by-ink hover:bg-by-green-soft"
          aria-label="Notifications"
        >
          <Bell className="size-5" />
        </button>
      </div>
    </header>
  )
}
