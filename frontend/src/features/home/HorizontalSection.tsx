import type { ReactNode } from 'react'
import { cn } from '@/utils/cn'

export type HorizontalSectionProps = {
  id?: string
  title: string
  subtitle?: string
  action?: ReactNode
  children: ReactNode
  className?: string
}

export function HorizontalSection({
  id,
  title,
  subtitle,
  action,
  children,
  className,
}: HorizontalSectionProps) {
  return (
    <section id={id} className={cn('text-left animate-fade-up', className)}>
      <div className="mb-3 flex items-end justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-by-ink">{title}</h3>
          {subtitle ? <p className="mt-0.5 text-sm text-by-muted">{subtitle}</p> : null}
        </div>
        {action}
      </div>
      <div className="scrollbar-hide -mx-4 flex gap-3 overflow-x-auto px-4 pb-2 snap-x snap-mandatory">
        {children}
      </div>
    </section>
  )
}
