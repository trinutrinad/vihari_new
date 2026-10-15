import type { InputHTMLAttributes } from 'react'
import { cn } from '@/utils/cn'

export type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  label?: string
  error?: string
  hint?: string
}

export function Input({
  className,
  label,
  error,
  hint,
  id,
  ...props
}: InputProps) {
  const inputId = id ?? props.name

  return (
    <label className="flex w-full flex-col gap-1.5 text-left">
      {label ? (
        <span className="text-sm font-medium text-by-ink">{label}</span>
      ) : null}
      <input
        id={inputId}
        className={cn(
          'h-11 w-full rounded-2xl border bg-white px-3 text-by-ink',
          'placeholder:text-by-muted/70',
          'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-by-green',
          error ? 'border-by-danger' : 'border-by-border',
          className,
        )}
        {...props}
      />
      {error ? <span className="text-xs text-by-danger">{error}</span> : null}
      {!error && hint ? <span className="text-xs text-by-muted">{hint}</span> : null}
    </label>
  )
}
