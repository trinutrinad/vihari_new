import type { HTMLAttributes, ReactNode } from 'react'
import { cn } from '@/utils/cn'

type BadgeTone = 'green' | 'saffron' | 'blue' | 'neutral'

export type BadgeProps = HTMLAttributes<HTMLSpanElement> & {
  tone?: BadgeTone
  children: ReactNode
}

const toneClasses: Record<BadgeTone, string> = {
  green: 'bg-by-green-soft text-by-green-dark',
  saffron: 'bg-by-saffron-soft text-by-saffron',
  blue: 'bg-by-blue-soft text-by-blue',
  neutral: 'bg-by-border/60 text-by-muted',
}

export function Badge({
  className,
  tone = 'green',
  children,
  ...props
}: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        toneClasses[tone],
        className,
      )}
      {...props}
    >
      {children}
    </span>
  )
}
