import { Link, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States'
import { ROUTES } from '@/constants/app'
import {
  fetchBusinessAccess,
  fetchBusinessBookings,
  fetchBusinessProperties,
  fetchBusinessSummary,
} from '@/services/business'
import { useAuthStore } from '@/store/auth'

function formatInr(amount: number) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

export function BusinessDashboardPage() {
  const navigate = useNavigate()
  const tokens = useAuthStore((state) => state.tokens)
  const user = useAuthStore((state) => state.user)

  const accessQuery = useQuery({
    queryKey: ['business-access'],
    queryFn: async () => {
      const response = await fetchBusinessAccess()
      return response.data
    },
    enabled: Boolean(tokens?.access_token),
  })

  const summaryQuery = useQuery({
    queryKey: ['business-summary'],
    queryFn: async () => {
      const response = await fetchBusinessSummary()
      return response.data
    },
    enabled: Boolean(tokens?.access_token) && accessQuery.data?.has_access === true,
  })

  const propertiesQuery = useQuery({
    queryKey: ['business-properties'],
    queryFn: async () => {
      const response = await fetchBusinessProperties()
      return response.data ?? []
    },
    enabled: Boolean(tokens?.access_token) && accessQuery.data?.has_access === true,
  })

  const bookingsQuery = useQuery({
    queryKey: ['business-bookings'],
    queryFn: async () => {
      const response = await fetchBusinessBookings({ limit: 20 })
      return response.data ?? []
    },
    enabled: Boolean(tokens?.access_token) && accessQuery.data?.has_access === true,
  })

  if (!tokens?.access_token) {
    return (
      <Card className="space-y-4 text-left">
        <h2 className="font-display text-2xl font-semibold text-by-ink">Business</h2>
        <p className="text-sm text-by-muted">
          Sign in with a business owner account to view property and booking summaries.
        </p>
        <Button onClick={() => navigate(ROUTES.login)}>Sign in</Button>
      </Card>
    )
  }

  if (accessQuery.isLoading) {
    return <LoadingState label="Loading business access…" />
  }

  if (accessQuery.isError) {
    return <ErrorState title="Could not load business access." />
  }

  if (!accessQuery.data?.has_access) {
    return (
      <Card className="space-y-4 text-left">
        <h2 className="font-display text-2xl font-semibold text-by-ink">Business</h2>
        <p className="text-sm text-by-muted">
          This account is a traveller profile. Use the demo owner login to explore the dashboard:
          <span className="mt-2 block font-mono text-xs text-by-ink">
            demo.owner@example.com / DemoOwner1!
          </span>
        </p>
        <div className="flex flex-wrap gap-2">
          <Button onClick={() => navigate(ROUTES.login)}>Switch account</Button>
          <Button variant="ghost" onClick={() => navigate(ROUTES.profile)}>
            Profile
          </Button>
        </div>
      </Card>
    )
  }

  const summary = summaryQuery.data
  const properties = propertiesQuery.data ?? []
  const bookings = bookingsQuery.data ?? []

  return (
    <div className="flex flex-col gap-5 text-left">
      <div>
        <h2 className="font-display text-2xl font-semibold text-by-ink">Business dashboard</h2>
        <p className="mt-1 text-sm text-by-muted">
          Owner-scoped mock overview for {user?.full_name ?? 'your'} properties.
        </p>
        {accessQuery.data.roles.length > 0 ? (
          <div className="mt-2 flex flex-wrap gap-2">
            {accessQuery.data.roles.map((role) => (
              <Badge key={role}>{role.replaceAll('_', ' ')}</Badge>
            ))}
          </div>
        ) : null}
      </div>

      {summaryQuery.isLoading ? <LoadingState label="Loading summary…" /> : null}
      {summaryQuery.isError ? <ErrorState title="Could not load summary." /> : null}

      {summary ? (
        <>
          <p className="text-xs text-by-muted">{summary.data_notice}</p>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Stat label="Hotels" value={String(summary.hotels_count)} />
            <Stat label="Restaurants" value={String(summary.restaurants_count)} />
            <Stat label="Guides" value={String(summary.guides_count)} />
            <Stat label="Captured revenue" value={formatInr(summary.revenue_captured_inr)} />
            <Stat label="Bookings" value={String(summary.bookings_total)} />
            <Stat label="Confirmed" value={String(summary.bookings_confirmed)} />
            <Stat label="Pending" value={String(summary.bookings_pending)} />
            <Stat label="Cancelled" value={String(summary.bookings_cancelled)} />
          </div>
        </>
      ) : null}

      <section className="space-y-3">
        <h3 className="font-display text-lg font-semibold text-by-ink">Your properties</h3>
        {propertiesQuery.isLoading ? <LoadingState label="Loading properties…" /> : null}
        {propertiesQuery.isError ? <ErrorState title="Could not load properties." /> : null}
        {!propertiesQuery.isLoading && properties.length === 0 ? (
          <EmptyState title="No properties linked" description="Seed owner links demo hotels, restaurants, and a guide." />
        ) : null}
        <ul className="space-y-2">
          {properties.map((property) => (
            <li key={`${property.resource_type}-${property.id}`}>
              <Card className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="font-medium text-by-ink">{property.name}</p>
                  <p className="text-xs uppercase tracking-wide text-by-muted">
                    {property.resource_type}
                    {property.city_name ? ` · ${property.city_name}` : ''}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {property.is_seed_data ? <Badge>SEED/DEMO</Badge> : null}
                  {property.href ? (
                    <Link
                      to={property.href}
                      className="text-sm font-medium text-by-green hover:underline"
                    >
                      View
                    </Link>
                  ) : null}
                </div>
              </Card>
            </li>
          ))}
        </ul>
      </section>

      <section className="space-y-3">
        <h3 className="font-display text-lg font-semibold text-by-ink">Recent bookings</h3>
        {bookingsQuery.isLoading ? <LoadingState label="Loading bookings…" /> : null}
        {bookingsQuery.isError ? <ErrorState title="Could not load bookings." /> : null}
        {!bookingsQuery.isLoading && bookings.length === 0 ? (
          <EmptyState
            title="No bookings yet"
            description="When travellers book your properties, they appear here."
          />
        ) : null}
        <ul className="space-y-2">
          {bookings.map((booking) => (
            <li key={booking.id}>
              <Card className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="font-medium text-by-ink">{booking.resource_title}</p>
                  <p className="text-xs text-by-muted">
                    {booking.booking_number} · {booking.resource_type} · {booking.status}
                  </p>
                </div>
                <p className="text-sm font-medium text-by-ink">{formatInr(booking.amount_inr)}</p>
              </Card>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <Card className="space-y-1">
      <p className="text-xs uppercase tracking-wide text-by-muted">{label}</p>
      <p className="font-display text-xl font-semibold text-by-ink">{value}</p>
    </Card>
  )
}
