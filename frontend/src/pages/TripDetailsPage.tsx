import { useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Share2, Trash2 } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States'
import { TripRouteMap } from '@/features/trips/TripRouteMap'
import { ROUTES } from '@/constants/app'
import { listPlaces } from '@/services/places'
import {
  addTripDay,
  addTripStop,
  deleteTrip,
  deleteTripDay,
  getTrip,
  removeTripStop,
  shareTrip,
  updateTrip,
} from '@/services/trips'
import { useAuthStore } from '@/store/auth'
import type { TripStatus } from '@/types/trips'

const STATUS_OPTIONS: TripStatus[] = ['draft', 'upcoming', 'active', 'completed', 'cancelled']

export function TripDetailsPage() {
  const { tripId = '' } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const tokens = useAuthStore((state) => state.tokens)
  const [placeQuery, setPlaceQuery] = useState('')
  const [activeDayId, setActiveDayId] = useState<string | null>(null)
  const [sharePath, setSharePath] = useState<string | null>(null)
  const [customStop, setCustomStop] = useState('')

  const tripQuery = useQuery({
    queryKey: ['trip', tripId],
    queryFn: async () => {
      const response = await getTrip(tripId)
      if (!response.data) throw new Error('Trip not found')
      return response.data
    },
    enabled: Boolean(tokens?.access_token && tripId),
  })

  const placesQuery = useQuery({
    queryKey: ['trip-place-picker', placeQuery],
    queryFn: async () => {
      const response = await listPlaces({ page: 1, page_size: 8, q: placeQuery || undefined })
      return response.data?.items ?? []
    },
    enabled: Boolean(tokens?.access_token && activeDayId),
  })

  const invalidate = async () => {
    await queryClient.invalidateQueries({ queryKey: ['trip', tripId] })
    await queryClient.invalidateQueries({ queryKey: ['trips'] })
  }

  const statusMutation = useMutation({
    mutationFn: (status: TripStatus) => updateTrip(tripId, { status }),
    onSuccess: invalidate,
  })

  const addDayMutation = useMutation({
    mutationFn: async () => {
      const next = (tripQuery.data?.days.reduce((max, day) => Math.max(max, day.day_number), 0) ?? 0) + 1
      return addTripDay(tripId, { day_number: next, title: `Day ${next}` })
    },
    onSuccess: invalidate,
  })

  const addStopMutation = useMutation({
    mutationFn: async (payload: { dayId: string; place_id?: string; custom_title?: string }) =>
      addTripStop(tripId, payload.dayId, {
        place_id: payload.place_id,
        custom_title: payload.custom_title,
        time_slot: 'Flexible',
      }),
    onSuccess: async () => {
      setCustomStop('')
      await invalidate()
    },
  })

  const removeStopMutation = useMutation({
    mutationFn: ({ dayId, stopId }: { dayId: string; stopId: string }) =>
      removeTripStop(tripId, dayId, stopId),
    onSuccess: invalidate,
  })

  const deleteDayMutation = useMutation({
    mutationFn: (dayId: string) => deleteTripDay(tripId, dayId),
    onSuccess: invalidate,
  })

  const deleteMutation = useMutation({
    mutationFn: () => deleteTrip(tripId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['trips'] })
      navigate(ROUTES.trips)
    },
  })

  const shareMutation = useMutation({
    mutationFn: () => shareTrip(tripId),
    onSuccess: async (response) => {
      const path = response.data?.share_path
      if (path) {
        setSharePath(path)
        const url = `${window.location.origin}${path}`
        await navigator.clipboard.writeText(url)
      }
      await invalidate()
    },
  })

  const selectedDayId = activeDayId ?? tripQuery.data?.days[0]?.id ?? null

  const dayOptions = useMemo(() => tripQuery.data?.days ?? [], [tripQuery.data?.days])

  if (!tokens?.access_token) {
    return (
      <ErrorState
        title="Sign in required"
        description="Trip details are private to your account."
        actionLabel="Sign in"
        onAction={() => navigate(ROUTES.login)}
      />
    )
  }

  if (tripQuery.isLoading) return <LoadingState label="Loading trip…" />
  if (tripQuery.isError || !tripQuery.data) {
    return (
      <ErrorState
        title="Trip not found"
        description="It may have been deleted or you do not have access."
        actionLabel="Back to trips"
        onAction={() => navigate(ROUTES.trips)}
      />
    )
  }

  const trip = tripQuery.data

  return (
    <div className="flex flex-col gap-5 text-left">
      <div className="space-y-3">
        <Link to={ROUTES.trips} className="text-sm font-medium text-by-green hover:underline">
          ← My Trips
        </Link>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="font-display text-3xl font-semibold text-by-ink">{trip.title}</h1>
            <p className="mt-1 text-sm text-by-muted">
              {trip.destination_summary || trip.origin_city || 'Custom itinerary'}
            </p>
          </div>
          <Badge tone="green">{trip.status}</Badge>
        </div>
        <div className="flex flex-wrap gap-2">
          {STATUS_OPTIONS.map((status) => (
            <Button
              key={status}
              size="sm"
              variant={trip.status === status ? 'primary' : 'ghost'}
              disabled={statusMutation.isPending}
              onClick={() => statusMutation.mutate(status)}
            >
              {status}
            </Button>
          ))}
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            size="sm"
            variant="secondary"
            leftIcon={<Share2 className="size-4" />}
            onClick={() => shareMutation.mutate()}
          >
            Share
          </Button>
          <Button
            size="sm"
            variant="danger"
            leftIcon={<Trash2 className="size-4" />}
            onClick={() => {
              if (window.confirm('Delete this trip?')) deleteMutation.mutate()
            }}
          >
            Delete
          </Button>
        </div>
        {sharePath ? (
          <p className="text-xs text-by-muted">
            Share link copied: <span className="font-medium text-by-ink">{sharePath}</span>
          </p>
        ) : null}
        <dl className="grid gap-2 sm:grid-cols-3 text-sm">
          <Meta label="Budget" value={trip.budget_inr != null ? `₹${trip.budget_inr.toLocaleString('en-IN')}` : '—'} />
          <Meta
            label="Estimated"
            value={
              trip.estimated_cost_inr != null
                ? `₹${trip.estimated_cost_inr.toLocaleString('en-IN')}`
                : '—'
            }
          />
          <Meta label="Stops" value={`${trip.stop_count} across ${trip.day_count} days`} />
        </dl>
      </div>

      <TripRouteMap points={trip.map_points} className="h-64" />

      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-lg font-semibold text-by-ink">Itinerary</h2>
        <Button size="sm" onClick={() => addDayMutation.mutate()} disabled={addDayMutation.isPending}>
          Add day
        </Button>
      </div>

      {dayOptions.length === 0 ? (
        <Card>
          <EmptyState title="No days yet" description="Add Day 1 to start building the itinerary." />
        </Card>
      ) : null}

      {dayOptions.map((day) => (
        <Card key={day.id} className="space-y-3">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div>
              <h3 className="font-semibold text-by-ink">
                Day {day.day_number}
                {day.title ? ` · ${day.title}` : ''}
              </h3>
              {day.notes ? <p className="mt-1 text-sm text-by-muted">{day.notes}</p> : null}
            </div>
            <div className="flex gap-2">
              <Button
                size="sm"
                variant={selectedDayId === day.id ? 'saffron' : 'ghost'}
                onClick={() => setActiveDayId(day.id)}
              >
                Add stops
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => deleteDayMutation.mutate(day.id)}
              >
                Remove day
              </Button>
            </div>
          </div>

          {day.places.length === 0 ? (
            <p className="text-sm text-by-muted">No stops yet.</p>
          ) : (
            <ul className="space-y-2">
              {day.places.map((stop) => (
                <li
                  key={stop.id}
                  className="flex flex-wrap items-start justify-between gap-2 rounded-xl bg-by-green-soft/60 px-3 py-2"
                >
                  <div>
                    {stop.place_id ? (
                      <Link
                        to={`/places/${stop.place_id}`}
                        className="text-sm font-medium text-by-ink hover:underline"
                      >
                        {stop.title}
                      </Link>
                    ) : (
                      <p className="text-sm font-medium text-by-ink">{stop.title}</p>
                    )}
                    <p className="text-xs text-by-muted">
                      {[stop.time_slot, stop.city_name, stop.estimated_cost_inr != null ? `₹${stop.estimated_cost_inr}` : null]
                        .filter(Boolean)
                        .join(' · ')}
                    </p>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() =>
                      removeStopMutation.mutate({ dayId: day.id, stopId: stop.id })
                    }
                  >
                    Remove
                  </Button>
                </li>
              ))}
            </ul>
          )}

          {selectedDayId === day.id ? (
            <div className="space-y-3 border-t border-by-border pt-3">
              <Input
                label="Search places to add"
                value={placeQuery}
                onChange={(event) => setPlaceQuery(event.target.value)}
                placeholder="Charminar, beach, temple…"
              />
              <div className="grid gap-2">
                {(placesQuery.data ?? []).map((place) => (
                  <button
                    key={place.id}
                    type="button"
                    className="rounded-xl border border-by-border px-3 py-2 text-left text-sm hover:bg-by-green-soft"
                    onClick={() =>
                      addStopMutation.mutate({ dayId: day.id, place_id: place.id })
                    }
                  >
                    <span className="font-medium text-by-ink">{place.name}</span>
                    <span className="mt-0.5 block text-xs text-by-muted">
                      {place.city_name}, {place.state_code}
                    </span>
                  </button>
                ))}
              </div>
              <div className="flex flex-wrap items-end gap-2">
                <Input
                  label="Custom stop"
                  value={customStop}
                  onChange={(event) => setCustomStop(event.target.value)}
                  placeholder="Local market / lunch"
                  className="min-w-[12rem] flex-1"
                />
                <Button
                  size="sm"
                  disabled={!customStop.trim() || addStopMutation.isPending}
                  onClick={() =>
                    addStopMutation.mutate({
                      dayId: day.id,
                      custom_title: customStop.trim(),
                    })
                  }
                >
                  Add custom
                </Button>
              </div>
            </div>
          ) : null}
        </Card>
      ))}
    </div>
  )
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-white px-3 py-2 border border-by-border">
      <dt className="text-xs uppercase tracking-wide text-by-muted">{label}</dt>
      <dd className="mt-1 font-medium text-by-ink">{value}</dd>
    </div>
  )
}
