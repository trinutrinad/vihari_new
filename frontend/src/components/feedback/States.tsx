import type { ReactNode } from 'react'
import { cn } from '@/utils/cn'
import { Button } from '@/components/ui/Button'

type StateProps = {
  title: string
  description?: string
  actionLabel?: string
  onAction?: () => void
  icon?: ReactNode
  className?: string
}

function StateShell({
  title,
  description,
  actionLabel,
  onAction,
  icon,
  className,
}: StateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center gap-3 px-6 py-12 text-center',
        className,
      )}
    >
      {icon}
      <h2 className="text-lg font-semibold text-by-ink">{title}</h2>
      {description ? <p className="max-w-sm text-sm text-by-muted">{description}</p> : null}
      {actionLabel && onAction ? (
        <Button onClick={onAction} className="mt-2">
          {actionLabel}
        </Button>
      ) : null}
    </div>
  )
}

export function EmptyState(props: StateProps) {
  return <StateShell {...props} />
}

export function ErrorState(props: StateProps) {
  return (
    <StateShell
      {...props}
      title={props.title || 'Something went wrong'}
    />
  )
}

export function LoadingState({
  label = 'Loading…',
  className,
}: {
  label?: string
  className?: string
}) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center gap-3 px-6 py-12 text-by-muted',
        className,
      )}
      role="status"
      aria-live="polite"
    >
      <div className="size-8 animate-spin rounded-full border-2 border-by-border border-t-by-green" />
      <span className="text-sm">{label}</span>
    </div>
  )
}
