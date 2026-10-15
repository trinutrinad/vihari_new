import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States'
import { ROUTES } from '@/constants/app'
import { listBookings } from '@/services/bookings'
import { useAuthStore } from '@/store/auth'
import type { BookingStatus } from '@/types/bookings'

const STATUS_FILTERS: Array<{ id: string; label: string; value?: BookingStatus }> = [
  { id: 'all', label: 'All' },
  { id: 'confirmed', label: 'Confirmed', value: 'confirmed' },
  { id: 'cancelled', label: 'Cancelled', value: 'cancelled' },
]

const TYPE_FILTERS = [
  { id: 'all', label: 'All types' },
  { id: 'hotel', label: 'Hotels' },
  { id: 'guide', label: 'Guides' },
  { id: 'activity', label: 'Activities' },
  { id: 'transport', label: 'Rides' },
  { id: 'restaurant', label: 'Food' },
] as const

export function BookingsPage() {
  const navigate = useNavigate()
  const tokens = useAuthStore((state) => state.tokens)
  const [status, setStatus] = useState<BookingStatus | undefined>()
  const [resourceType, setResourceType] = useState<string | undefined>()

  const bookingsQuery = useQuery({
    queryKey: ['bookings', status ?? 'all', resourceType ?? 'all'],
    queryFn: async () => {
      const response = await listBookings({
        status,
        resource_type: resourceType,
      })
      return response.data ?? []
    },
    enabled: Boolean(tokens?.access_token),
  })

  const bookings = useMemo(() => bookingsQuery.data ?? [], [bookingsQuery.data])

  if (!tokens?.access_token) {
    return (
      <Card className="space-y-4 text-left">
        <h2 className="font-display text-2xl font-semibold text-by-ink">Bookings</h2>
        <p className="text-sm text-by-muted">
          Sign in to create mock bookings for hotels, guides, activities, rides, and food.
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
      <div>
        <h2 className="font-display text-2xl font-semibold text-by-ink">Bookings</h2>
        <p className="mt-1 text-sm text-by-muted">
          Mock confirmations only — payments arrive in Phase 17.
        </p>
      </div>

      <div className="scrollbar-hide -mx-4 flex gap-2 overflow-x-auto px-4">
        {STATUS_FILTERS.map((item) => (
          <Button
            key={item.id}
            size="sm"
            variant={status === item.value ? 'primary' : 'ghost'}
            onClick={() => setStatus(item.value)}
          >
            {item.label}
          </Button>
        ))}
      </div>

      <div className="flex flex-wrap gap-2">
        {TYPE_FILTERS.map((item) => (
          <Button
            key={item.id}
            size="sm"
            variant={
              (item.id === 'all' && !resourceType) || resourceType === item.id
                ? 'saffron'
                : 'ghost'
            }
            onClick={() =>
              setResourceType(item.id === 'all' ? undefined : item.id)
            }
          >
            {item.label}
          </Button>
        ))}
      </div>

      {bookingsQuery.isLoading ? <LoadingState label="Loading bookings…" /> : null}
      {bookingsQuery.isError ? (
        <ErrorState
          title="Could not load bookings"
          description="Retry after confirming you are signed in."
          actionLabel="Retry"
          onAction={() => void bookingsQuery.refetch()}
        />
      ) : null}

      {!bookingsQuery.isLoading && bookings.length === 0 ? (
        <Card>
          <EmptyState
            title="No bookings yet"
            description="Open a hotel, guide, activity, ride, or restaurant and create a mock booking."
            actionLabel="Browse hotels"
            onAction={() => navigate(ROUTES.hotels)}
          />
        </Card>
      ) : null}

      {bookings.length > 0 ? (
        <ul className="space-y-3">
          {bookings.map((booking) => (
            <li key={booking.id}>
              <Link
                to={`/bookings/${booking.id}`}
                className="block rounded-[1.25rem] border border-by-border bg-white p-4 shadow-[var(--shadow-by-card)] transition hover:border-by-saffron/40"
              >
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <p className="font-semibold text-by-ink">{booking.resource_title}</p>
                    <p className="mt-1 text-xs text-by-muted">
                      {booking.booking_number} · {booking.resource_type}
                      {booking.location_text ? ` · ${booking.location_text}` : ''}
                    </p>
                  </div>
                  <div className="text-right">
                    <Badge
                      tone={
                        booking.status === 'cancelled'
                          ? 'neutral'
                          : booking.status === 'confirmed'
                            ? 'green'
                            : 'blue'
                      }
                    >
                      {booking.status}
                    </Badge>
                    <p className="mt-2 text-sm font-medium text-by-ink">
                      ₹{booking.amount_inr.toLocaleString('en-IN')}
                    </p>
                  </div>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  )
}
