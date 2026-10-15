import { Search } from 'lucide-react'
import type { InputHTMLAttributes } from 'react'
import { cn } from '@/utils/cn'

export type SearchBarProps = InputHTMLAttributes<HTMLInputElement> & {
  onSubmitSearch?: (value: string) => void
}

export function SearchBar({
  className,
  placeholder = 'Search places, temples, hotels, food...',
  onSubmitSearch,
  ...props
}: SearchBarProps) {
  return (
    <form
      className={cn(
        'flex h-12 items-center gap-2 rounded-2xl border border-by-border bg-white px-3 shadow-sm',
        className,
      )}
      onSubmit={(event) => {
        event.preventDefault()
        const form = event.currentTarget
        const data = new FormData(form)
        const value = String(data.get('q') ?? '')
        onSubmitSearch?.(value)
      }}
    >
      <Search className="size-5 shrink-0 text-by-green" aria-hidden />
      <input
        name="q"
        type="search"
        placeholder={placeholder}
        className="h-full w-full bg-transparent text-sm text-by-ink placeholder:text-by-muted/80 focus-visible:outline-none"
        {...props}
      />
    </form>
  )
}
