import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { CalendarDays, MapPinned, Plus } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States'
import { ROUTES } from '@/constants/app'
import { createTrip, listTrips } from '@/services/trips'
import { useAuthStore } from '@/store/auth'
import type { TripStatus } from '@/types/trips'

const STATUS_FILTERS: Array<{ id: string; label: string; value?: TripStatus }> = [
  { id: 'all', label: 'All' },
  { id: 'draft', label: 'Draft', value: 'draft' },
  { id: 'upcoming', label: 'Upcoming', value: 'upcoming' },
  { id: 'active', label: 'Active', value: 'active' },
  { id: 'completed', label: 'Completed', value: 'completed' },
]

export function TripsPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const tokens = useAuthStore((state) => state.tokens)
  const [status, setStatus] = useState<TripStatus | undefined>()
  const [showForm, setShowForm] = useState(false)
  const [title, setTitle] = useState('')
  const [origin, setOrigin] = useState('')
  const [destination, setDestination] = useState('')
  const [budget, setBudget] = useState('')
  const [formError, setFormError] = useState<string | null>(null)

  const tripsQuery = useQuery({
    queryKey: ['trips', status ?? 'all'],
    queryFn: async () => {
      const response = await listTrips(status)
      return response.data ?? []
    },
    enabled: Boolean(tokens?.access_token),
  })

  const createMutation = useMutation({
    mutationFn: async () => {
      const cleaned = title.trim()
      if (cleaned.length < 2) throw new Error('Title needs at least 2 characters')
      return createTrip({
        title: cleaned,
        origin_city: origin.trim() || undefined,
        destination_summary: destination.trim() || undefined,
        budget_inr: budget ? Number(budget) : undefined,
        status: 'draft',
        days: [{ day_number: 1, title: 'Day 1' }],
      })
    },
    onSuccess: async (response) => {
      setFormError(null)
      setShowForm(false)
      setTitle('')
      setOrigin('')
      setDestination('')
      setBudget('')
      await queryClient.invalidateQueries({ queryKey: ['trips'] })
      if (response.data?.id) navigate(`/trips/${response.data.id}`)
    },
    onError: (error: Error) => setFormError(error.message || 'Could not create trip'),
  })

  const trips = useMemo(() => tripsQuery.data ?? [], [tripsQuery.data])

  if (!tokens?.access_token) {
    return (
      <Card className="space-y-4 text-left">
        <h2 className="font-display text-2xl font-semibold text-by-ink">My Trips</h2>
        <p className="text-sm text-by-muted">
          Sign in to create itineraries, add stops, and share trip routes.
        </p>
        <div className="flex flex-wrap gap-2">
          <Button onClick={() => navigate(ROUTES.login)}>Sign in</Button>
          <Button variant="ghost" onClick={() => navigate(ROUTES.register)}>
            Create account
          </Button>
        </div>
      </Card>
    )
  }

  return (
    <div className="flex flex-col gap-5 text-left">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="font-display text-2xl font-semibold text-by-ink">My Trips</h2>
          <p className="mt-1 text-sm text-by-muted">
            Plan day-by-day itineraries and preview routes on the map.
          </p>
        </div>
        <Button
          size="sm"
          leftIcon={<Plus className="size-4" />}
          onClick={() => setShowForm((value) => !value)}
        >
          New trip
        </Button>
      </div>

      {showForm ? (
        <Card className="space-y-3">
          <h3 className="text-sm font-semibold text-by-ink">Create trip</h3>
          <Input
            label="Title"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="Hyderabad weekend"
          />
          <div className="grid gap-3 sm:grid-cols-2">
            <Input
              label="Origin city"
              value={origin}
              onChange={(event) => setOrigin(event.target.value)}
              placeholder="Hyderabad"
            />
            <Input
              label="Destination summary"
              value={destination}
              onChange={(event) => setDestination(event.target.value)}
              placeholder="City + nearby"
            />
          </div>
          <Input
            label="Budget (₹)"
            type="number"
            min={0}
            value={budget}
            onChange={(event) => setBudget(event.target.value)}
          />
          {formError ? <p className="text-sm text-by-danger">{formError}</p> : null}
          <div className="flex gap-2">
            <Button
              size="sm"
              disabled={createMutation.isPending}
              onClick={() => createMutation.mutate()}
            >
              {createMutation.isPending ? 'Creating…' : 'Create'}
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setShowForm(false)}>
              Cancel
            </Button>
          </div>
        </Card>
      ) : null}

      <div className="scrollbar-hide -mx-4 flex gap-2 overflow-x-auto px-4">
        {STATUS_FILTERS.map((item) => (
          <Button
            key={item.id}
            size="sm"
            variant={(status ?? undefined) === item.value ? 'primary' : 'ghost'}
            onClick={() => setStatus(item.value)}
          >
            {item.label}
          </Button>
        ))}
      </div>

      {tripsQuery.isLoading ? <LoadingState label="Loading trips…" /> : null}
      {tripsQuery.isError ? (
        <ErrorState
          title="Could not load trips"
          description="Check that you are signed in and the API is running."
          actionLabel="Retry"
          onAction={() => void tripsQuery.refetch()}
        />
      ) : null}

      {!tripsQuery.isLoading && trips.length === 0 ? (
        <Card>
          <EmptyState
            title="No trips yet"
            description="Create a draft trip, then add places day by day."
            actionLabel="New trip"
            onAction={() => setShowForm(true)}
          />
        </Card>
      ) : null}

      <div className="grid gap-3">
        {trips.map((trip) => (
          <Link key={trip.id} to={`/trips/${trip.id}`}>
            <Card className="transition hover:border-by-green/40 hover:shadow-[var(--shadow-by-card)]">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div>
                  <h3 className="text-lg font-semibold text-by-ink">{trip.title}</h3>
                  <p className="mt-1 text-sm text-by-muted">
                    {trip.destination_summary || trip.origin_city || 'Itinerary'}
                  </p>
                </div>
                <Badge tone={statusTone(trip.status)}>{trip.status}</Badge>
              </div>
              <div className="mt-3 flex flex-wrap gap-3 text-xs text-by-muted">
                <span className="inline-flex items-center gap-1">
                  <CalendarDays className="size-3.5" aria-hidden />
                  {formatDates(trip.start_date, trip.end_date)}
                </span>
                <span className="inline-flex items-center gap-1">
                  <MapPinned className="size-3.5" aria-hidden />
                  {trip.day_count} day{trip.day_count === 1 ? '' : 's'} · {trip.stop_count}{' '}
                  stop{trip.stop_count === 1 ? '' : 's'}
                </span>
                {trip.budget_inr != null ? (
                  <span>Budget ₹{trip.budget_inr.toLocaleString('en-IN')}</span>
                ) : null}
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}

function formatDates(start: string | null, end: string | null) {
  if (!start && !end) return 'Dates TBD'
  if (start && end) return `${start} → ${end}`
  return start || end || 'Dates TBD'
}

function statusTone(status: string): 'green' | 'saffron' | 'blue' | 'neutral' {
  if (status === 'active' || status === 'upcoming') return 'green'
  if (status === 'draft') return 'saffron'
  if (status === 'completed') return 'blue'
  return 'neutral'
}
