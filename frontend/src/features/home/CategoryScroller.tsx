import type { HomeCategory } from '@/types/place'
import { cn } from '@/utils/cn'

export type CategoryScrollerProps = {
  categories: HomeCategory[]
  activeId?: string | null
  onSelect?: (category: HomeCategory) => void
}

export function CategoryScroller({
  categories,
  activeId,
  onSelect,
}: CategoryScrollerProps) {
  return (
    <div className="scrollbar-hide -mx-4 flex gap-2 overflow-x-auto px-4 pb-1">
      {categories.map((category) => {
        const active = category.id === activeId
        return (
          <button
            key={category.id}
            type="button"
            onClick={() => onSelect?.(category)}
            className={cn(
              'shrink-0 rounded-full border px-4 py-2 text-sm font-medium transition',
              'active:scale-95',
              active
                ? 'border-by-green bg-by-green text-white shadow-sm'
                : 'border-by-border bg-white text-by-ink hover:border-by-green hover:text-by-green',
            )}
          >
            {category.label}
          </button>
        )
      })}
    </div>
  )
}
