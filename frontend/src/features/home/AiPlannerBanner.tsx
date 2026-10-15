import { Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/Button'

export type AiPlannerBannerProps = {
  onPlan?: () => void
}

export function AiPlannerBanner({ onPlan }: AiPlannerBannerProps) {
  return (
    <section className="animate-fade-up overflow-hidden rounded-[1.25rem] bg-gradient-to-br from-by-green via-by-green to-by-green-dark p-5 text-white shadow-[var(--shadow-by-card)]">
      <div className="flex items-start gap-3">
        <span className="rounded-2xl bg-white/15 p-2.5">
          <Sparkles className="size-5" aria-hidden />
        </span>
        <div className="min-w-0 flex-1">
          <h3 className="font-display text-xl font-semibold">AI Trip Planner</h3>
          <p className="mt-1 max-w-xl text-sm text-white/90">
            “I have ₹10,000 and 3 days from Hyderabad — peaceful nature and good food.”
            Get a day-by-day plan with stays, food, and budget.
          </p>
          <Button
            variant="saffron"
            size="sm"
            className="mt-4"
            onClick={onPlan}
            title="Open the AI trip planner"
          >
            Start planning
          </Button>
        </div>
      </div>
    </section>
  )
}
