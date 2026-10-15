import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { ErrorState, LoadingState } from '@/components/feedback/States'
import { TripRouteMap } from '@/features/trips/TripRouteMap'
import { ROUTES } from '@/constants/app'
import { getSharedTrip } from '@/services/trips'

export function SharedTripPage() {
  const { shareCode = '' } = useParams()

  const query = useQuery({
    queryKey: ['shared-trip', shareCode],
    queryFn: async () => {
      const response = await getSharedTrip(shareCode)
      if (!response.data) throw new Error('Not found')
      return response.data
    },
    enabled: Boolean(shareCode),
  })

  if (query.isLoading) return <LoadingState label="Loading shared trip…" />
  if (query.isError || !query.data) {
    return (
      <ErrorState
        title="Shared trip unavailable"
        description="The link may be invalid or the trip was deleted."
        actionLabel="Go home"
        onAction={() => {
          window.location.href = ROUTES.home
        }}
      />
    )
  }

  const trip = query.data

  return (
    <div className="flex flex-col gap-5 text-left">
      <div>
        <Badge tone="blue">Shared itinerary</Badge>
        <h1 className="mt-2 font-display text-3xl font-semibold text-by-ink">{trip.title}</h1>
        <p className="mt-1 text-sm text-by-muted">
          {trip.destination_summary || trip.origin_city || 'Trip overview'}
        </p>
      </div>

      <TripRouteMap points={trip.map_points} className="h-64" />

      {trip.days.map((day) => (
        <Card key={day.id} className="space-y-2">
          <h2 className="font-semibold text-by-ink">
            Day {day.day_number}
            {day.title ? ` · ${day.title}` : ''}
          </h2>
          <ul className="space-y-2">
            {day.places.map((stop) => (
              <li key={stop.id} className="rounded-xl bg-by-green-soft/50 px-3 py-2 text-sm">
                {stop.place_id ? (
                  <Link to={`/places/${stop.place_id}`} className="font-medium hover:underline">
                    {stop.title}
                  </Link>
                ) : (
                  <span className="font-medium">{stop.title}</span>
                )}
                {stop.time_slot ? (
                  <span className="mt-0.5 block text-xs text-by-muted">{stop.time_slot}</span>
                ) : null}
              </li>
            ))}
          </ul>
        </Card>
      ))}

      <Link to={ROUTES.trips} className="text-sm font-medium text-by-green hover:underline">
        Plan your own trip →
      </Link>
    </div>
  )
}
