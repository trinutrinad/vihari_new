import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Sparkles } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { ErrorState, LoadingState } from '@/components/feedback/States'
import { ROUTES } from '@/constants/app'
import { aiChat, listAiAgents, planTrip } from '@/services/ai'
import { useAuthStore } from '@/store/auth'
import type { PlanTripResult } from '@/types/ai'

const INTERESTS = [
  'nature',
  'food',
  'beach',
  'temple',
  'heritage',
  'mountain',
  'adventure',
  'peaceful',
] as const

export function PlannerPage() {
  const navigate = useNavigate()
  const tokens = useAuthStore((state) => state.tokens)
  const [origin, setOrigin] = useState('Hyderabad')
  const [destination, setDestination] = useState('')
  const [days, setDays] = useState('3')
  const [budget, setBudget] = useState('10000')
  const [prompt, setPrompt] = useState(
    'peaceful nature and good food',
  )
  const [selected, setSelected] = useState<string[]>(['nature', 'food'])
  const [plan, setPlan] = useState<PlanTripResult | null>(null)
  const [chatInput, setChatInput] = useState('')
  const [chatLog, setChatLog] = useState<Array<{ role: 'user' | 'assistant'; text: string }>>(
    [],
  )
  const [conversationId, setConversationId] = useState<string | undefined>()

  const agentsQuery = useQuery({
    queryKey: ['ai-agents'],
    queryFn: async () => {
      const response = await listAiAgents()
      return response.data ?? []
    },
  })

  const planMutation = useMutation({
    mutationFn: async (save: boolean) => {
      const response = await planTrip({
        origin_city: origin.trim(),
        days: Number(days) || 3,
        budget_inr: budget ? Number(budget) : undefined,
        interests: selected,
        destination_hint: destination.trim() || undefined,
        prompt: prompt.trim() || undefined,
        save,
      })
      if (!response.data) throw new Error('Planner failed')
      return response.data
    },
    onSuccess: (data) => {
      setPlan(data)
      if (data.trip?.id) navigate(`/trips/${data.trip.id}`)
    },
  })

  const chatMutation = useMutation({
    mutationFn: async (message: string) => {
      const response = await aiChat(message, conversationId)
      if (!response.data) throw new Error('Chat failed')
      return response.data
    },
    onSuccess: (data, message) => {
      setConversationId(data.conversation_id)
      setChatLog((prev) => [
        ...prev,
        { role: 'user', text: message },
        { role: 'assistant', text: data.reply },
      ])
      setChatInput('')
    },
  })

  const interestButtons = useMemo(() => INTERESTS, [])

  function toggleInterest(value: string) {
    setSelected((prev) =>
      prev.includes(value) ? prev.filter((item) => item !== value) : [...prev, value],
    )
  }

  return (
    <div className="flex flex-col gap-5 text-left">
      <div>
        <div className="flex items-center gap-2">
          <Sparkles className="size-5 text-by-saffron" aria-hidden />
          <h2 className="font-display text-2xl font-semibold text-by-ink">AI Trip Planner</h2>
        </div>
        <p className="mt-1 text-sm text-by-muted">
          Multi-agent mock planner (destination, hotel, food, guide, transport, weather,
          safety, budget → final planner). Live LLM vendors arrive later.{' '}
          <Link className="text-by-green hover:underline" to={ROUTES.ask}>
            Ask with RAG sources
          </Link>
        </p>
      </div>

      {(agentsQuery.data?.length ?? 0) > 0 ? (
        <Card className="space-y-2">
          <h3 className="text-sm font-semibold text-by-ink">Agent pipeline</h3>
          <div className="flex flex-wrap gap-2">
            {agentsQuery.data?.map((agent) => (
              <Badge key={agent.name} tone={agent.status === 'live' ? 'green' : 'neutral'}>
                {agent.name}
              </Badge>
            ))}
          </div>
        </Card>
      ) : null}

      <Card className="space-y-3">
        <div className="grid gap-3 sm:grid-cols-2">
          <Input
            label="From"
            value={origin}
            onChange={(event) => setOrigin(event.target.value)}
            placeholder="Hyderabad"
          />
          <Input
            label="Destination hint"
            value={destination}
            onChange={(event) => setDestination(event.target.value)}
            placeholder="Goa, Jaipur, Manali…"
          />
          <Input
            label="Days"
            type="number"
            min={1}
            max={14}
            value={days}
            onChange={(event) => setDays(event.target.value)}
          />
          <Input
            label="Budget (₹)"
            type="number"
            min={0}
            value={budget}
            onChange={(event) => setBudget(event.target.value)}
          />
        </div>
        <Input
          label="Describe your trip"
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          placeholder="I have 3 days and want peaceful nature + good food"
        />
        <div>
          <p className="mb-2 text-sm font-medium text-by-ink">Interests</p>
          <div className="flex flex-wrap gap-2">
            {interestButtons.map((item) => (
              <Button
                key={item}
                size="sm"
                variant={selected.includes(item) ? 'saffron' : 'ghost'}
                onClick={() => toggleInterest(item)}
              >
                {item}
              </Button>
            ))}
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            disabled={planMutation.isPending || origin.trim().length < 2}
            onClick={() => planMutation.mutate(false)}
          >
            {planMutation.isPending ? 'Planning…' : 'Preview plan'}
          </Button>
          <Button
            variant="secondary"
            disabled={planMutation.isPending || origin.trim().length < 2}
            onClick={() => {
              if (!tokens?.access_token) {
                navigate(ROUTES.login)
                return
              }
              planMutation.mutate(true)
            }}
          >
            Save as trip
          </Button>
        </div>
        {!tokens?.access_token ? (
          <p className="text-xs text-by-muted">
            Preview works without login. Saving requires{' '}
            <Link to={ROUTES.login} className="text-by-green hover:underline">
              sign in
            </Link>
            .
          </p>
        ) : null}
      </Card>

      {planMutation.isPending ? <LoadingState label="Building itinerary…" /> : null}
      {planMutation.isError ? (
        <ErrorState
          title="Planner unavailable"
          description="Start the API and seed data, then retry."
          actionLabel="Retry preview"
          onAction={() => planMutation.mutate(false)}
        />
      ) : null}

      {plan ? (
        <Card className="space-y-4">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div>
              <h3 className="text-xl font-semibold text-by-ink">{plan.title}</h3>
              <p className="mt-1 text-sm text-by-muted">{plan.summary}</p>
            </div>
            <Badge tone="blue">{plan.provider}/{plan.model}</Badge>
          </div>
          <p className="text-xs text-by-muted">{plan.notice}</p>
          {plan.budget_note ? (
            <p className="rounded-xl bg-by-saffron-soft px-3 py-2 text-sm text-by-saffron">
              {plan.budget_note}
            </p>
          ) : null}
          <dl className="grid gap-2 sm:grid-cols-3 text-sm">
            <Meta
              label="Estimate"
              value={
                plan.estimated_cost_inr != null
                  ? `₹${plan.estimated_cost_inr.toLocaleString('en-IN')}`
                  : '—'
              }
            />
            <Meta label="Destination" value={plan.destination_summary} />
            <Meta
              label="Agents"
              value={String(plan.agent_trace?.length ?? 0)}
            />
          </dl>

          {(plan.agent_trace?.length ?? 0) > 0 ? (
            <div className="space-y-2">
              <h4 className="text-sm font-semibold text-by-ink">Agent trace</h4>
              <ol className="space-y-1.5">
                {plan.agent_trace?.map((step, index) => (
                  <li
                    key={`${step.agent}-${index}`}
                    className="rounded-xl bg-by-green-soft/50 px-3 py-2 text-sm"
                  >
                    <span className="font-medium text-by-ink">
                      {index + 1}. {step.agent}
                    </span>
                    <span className="text-by-muted"> — {step.summary}</span>
                    {!step.ok ? (
                      <Badge tone="saffron" className="ml-2">
                        partial
                      </Badge>
                    ) : null}
                  </li>
                ))}
              </ol>
            </div>
          ) : null}

          {plan.days.map((day) => (
            <div key={day.day_number} className="rounded-xl border border-by-border p-3">
              <h4 className="font-semibold text-by-ink">
                Day {day.day_number}
                {day.title ? ` · ${day.title}` : ''}
              </h4>
              {day.notes ? <p className="mt-1 text-xs text-by-muted">{day.notes}</p> : null}
              <ul className="mt-2 space-y-1.5">
                {day.places.map((stop, index) => (
                  <li key={`${day.day_number}-${index}`} className="text-sm">
                    <span className="font-medium text-by-ink">{stop.title}</span>
                    <span className="text-by-muted">
                      {' '}
                      · {[stop.time_slot, stop.city].filter(Boolean).join(' · ')}
                    </span>
                    {stop.place_id ? (
                      <Link
                        to={`/places/${stop.place_id}`}
                        className="ml-2 text-xs text-by-blue hover:underline"
                      >
                        View
                      </Link>
                    ) : null}
                  </li>
                ))}
              </ul>
            </div>
          ))}

          {(plan.hotels.length > 0 || plan.restaurants.length > 0) ? (
            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <h4 className="text-sm font-semibold text-by-ink">Stay ideas (demo)</h4>
                <ul className="mt-2 space-y-1 text-sm text-by-muted">
                  {plan.hotels.map((hotel) => (
                    <li key={hotel.id}>
                      {hotel.name}
                      {hotel.starting_price_inr != null
                        ? ` · from ₹${hotel.starting_price_inr.toLocaleString('en-IN')}`
                        : ''}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-by-ink">Food ideas (demo)</h4>
                <ul className="mt-2 space-y-1 text-sm text-by-muted">
                  {plan.restaurants.map((item) => (
                    <li key={item.id}>
                      {item.name}
                      {item.cuisine_tags ? ` · ${item.cuisine_tags}` : ''}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : null}

          {(plan.guides?.length ?? 0) > 0 || (plan.transport?.length ?? 0) > 0 ? (
            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <h4 className="text-sm font-semibold text-by-ink">Guides (demo)</h4>
                <ul className="mt-2 space-y-1 text-sm text-by-muted">
                  {(plan.guides ?? []).map((guide) => (
                    <li key={guide.id}>
                      {guide.name}
                      {guide.price_per_day_inr != null
                        ? ` · ₹${guide.price_per_day_inr.toLocaleString('en-IN')}/day`
                        : ''}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-by-ink">Transport (demo)</h4>
                <ul className="mt-2 space-y-1 text-sm text-by-muted">
                  {(plan.transport ?? []).slice(0, 4).map((item) => (
                    <li key={item.id}>
                      {item.name}
                      {item.base_fare_inr != null ? ` · from ₹${item.base_fare_inr}` : ''}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : null}

          {plan.weather ? (
            <div className="rounded-xl border border-by-border p-3">
              <h4 className="text-sm font-semibold text-by-ink">Weather (mock)</h4>
              <p className="mt-1 text-xs text-by-muted">{plan.weather.disclaimer}</p>
              <ul className="mt-2 space-y-1 text-sm text-by-muted">
                {plan.weather.days.map((day) => (
                  <li key={day.day}>
                    Day {day.day}: {day.summary} ({day.temp_c_low}–{day.temp_c_high}°C)
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {plan.safety ? (
            <div className="rounded-xl border border-by-border p-3">
              <h4 className="text-sm font-semibold text-by-ink">Safety notes</h4>
              <p className="mt-1 text-xs text-by-muted">{plan.safety.disclaimer}</p>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-by-muted">
                {plan.safety.tips.map((tip) => (
                  <li key={tip}>{tip}</li>
                ))}
              </ul>
            </div>
          ) : null}

          {plan.booking ? (
            <p className="rounded-xl bg-by-blue-soft px-3 py-2 text-sm text-by-blue">
              {plan.booking.message}
            </p>
          ) : null}
        </Card>
      ) : null}

      <Card className="space-y-3">
        <h3 className="text-lg font-semibold text-by-ink">Ask the travel assistant</h3>
        <div className="space-y-2">
          {chatLog.map((item, index) => (
            <p
              key={`${item.role}-${index}`}
              className={
                item.role === 'user'
                  ? 'rounded-xl bg-by-green-soft px-3 py-2 text-sm'
                  : 'rounded-xl bg-by-blue-soft px-3 py-2 text-sm'
              }
            >
              <span className="font-medium">{item.role === 'user' ? 'You' : 'Assistant'}: </span>
              {item.text}
            </p>
          ))}
        </div>
        <div className="flex flex-wrap gap-2">
          <Input
            value={chatInput}
            onChange={(event) => setChatInput(event.target.value)}
            placeholder="Any tips for a budget weekend?"
            className="min-w-[14rem] flex-1"
          />
          <Button
            size="sm"
            disabled={!chatInput.trim() || chatMutation.isPending}
            onClick={() => chatMutation.mutate(chatInput.trim())}
          >
            Send
          </Button>
        </div>
      </Card>
    </div>
  )
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-by-border bg-white px-3 py-2">
      <dt className="text-xs uppercase tracking-wide text-by-muted">{label}</dt>
      <dd className="mt-1 font-medium text-by-ink">{value}</dd>
    </div>
  )
}
