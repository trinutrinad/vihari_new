import type { ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States'
import { ROUTES } from '@/constants/app'
import {
  fetchAdminAccess,
  fetchAdminBookings,
  fetchAdminPayments,
  fetchAdminSummary,
  fetchAdminTickets,
  fetchAdminUsers,
} from '@/services/admin'
import { useAuthStore } from '@/store/auth'

function formatInr(amount: number) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

export function AdminDashboardPage() {
  const navigate = useNavigate()
  const tokens = useAuthStore((state) => state.tokens)
  const user = useAuthStore((state) => state.user)

  const accessQuery = useQuery({
    queryKey: ['admin-access'],
    queryFn: async () => {
      const response = await fetchAdminAccess()
      return response.data
    },
    enabled: Boolean(tokens?.access_token),
  })

  const enabled = Boolean(tokens?.access_token) && accessQuery.data?.has_access === true

  const summaryQuery = useQuery({
    queryKey: ['admin-summary'],
    queryFn: async () => {
      const response = await fetchAdminSummary()
      return response.data
    },
    enabled,
  })

  const usersQuery = useQuery({
    queryKey: ['admin-users'],
    queryFn: async () => {
      const response = await fetchAdminUsers({ limit: 20 })
      return response.data ?? []
    },
    enabled,
  })

  const bookingsQuery = useQuery({
    queryKey: ['admin-bookings'],
    queryFn: async () => {
      const response = await fetchAdminBookings({ limit: 15 })
      return response.data ?? []
    },
    enabled,
  })

  const paymentsQuery = useQuery({
    queryKey: ['admin-payments'],
    queryFn: async () => {
      const response = await fetchAdminPayments({ limit: 15 })
      return response.data ?? []
    },
    enabled,
  })

  const ticketsQuery = useQuery({
    queryKey: ['admin-tickets'],
    queryFn: async () => {
      const response = await fetchAdminTickets({ limit: 15 })
      return response.data ?? []
    },
    enabled,
  })

  if (!tokens?.access_token) {
    return (
      <Card className="space-y-4 text-left">
        <h2 className="font-display text-2xl font-semibold text-by-ink">Admin</h2>
        <p className="text-sm text-by-muted">
          Sign in with a platform admin account to view system-wide metrics.
        </p>
        <Button onClick={() => navigate(ROUTES.login)}>Sign in</Button>
      </Card>
    )
  }

  if (accessQuery.isLoading) {
    return <LoadingState label="Loading admin access…" />
  }

  if (accessQuery.isError) {
    return <ErrorState title="Could not load admin access." />
  }

  if (!accessQuery.data?.has_access) {
    return (
      <Card className="space-y-4 text-left">
        <h2 className="font-display text-2xl font-semibold text-by-ink">Admin</h2>
        <p className="text-sm text-by-muted">
          This account does not have admin privileges. Use the demo admin login:
          <span className="mt-2 block font-mono text-xs text-by-ink">
            demo.admin@example.com / DemoAdmin1!
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
  const users = usersQuery.data ?? []
  const bookings = bookingsQuery.data ?? []
  const payments = paymentsQuery.data ?? []
  const tickets = ticketsQuery.data ?? []

  return (
    <div className="flex flex-col gap-5 text-left">
      <div>
        <h2 className="font-display text-2xl font-semibold text-by-ink">Admin dashboard</h2>
        <p className="mt-1 text-sm text-by-muted">
          Platform overview for {user?.full_name ?? 'ops'}. Deep CRUD also available via Django
          Admin in <code className="text-xs">/admin</code>.
        </p>
        <div className="mt-2 flex flex-wrap gap-2">
          {accessQuery.data.roles.map((role) => (
            <Badge key={role}>{role.replaceAll('_', ' ')}</Badge>
          ))}
        </div>
      </div>

      {summaryQuery.isLoading ? <LoadingState label="Loading summary…" /> : null}
      {summaryQuery.isError ? <ErrorState title="Could not load summary." /> : null}

      {summary ? (
        <>
          <p className="text-xs text-by-muted">{summary.data_notice}</p>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Stat label="Users" value={String(summary.users_total)} />
            <Stat label="Active users" value={String(summary.users_active)} />
            <Stat label="Places" value={String(summary.places_total)} />
            <Stat label="Hotels" value={String(summary.hotels_total)} />
            <Stat label="Restaurants" value={String(summary.restaurants_total)} />
            <Stat label="Guides" value={String(summary.guides_total)} />
            <Stat label="Activities" value={String(summary.activities_total)} />
            <Stat label="Seed entities" value={String(summary.seed_entities_total)} />
            <Stat label="Bookings" value={String(summary.bookings_total)} />
            <Stat label="Open bookings" value={String(summary.bookings_open)} />
            <Stat label="Captured payments" value={String(summary.payments_captured_total)} />
            <Stat label="Revenue captured" value={formatInr(summary.revenue_captured_inr)} />
            <Stat label="Open tickets" value={String(summary.support_tickets_open)} />
          </div>
        </>
      ) : null}

      <ListSection
        title="Recent users"
        loading={usersQuery.isLoading}
        error={usersQuery.isError}
        empty={users.length === 0}
      >
        {users.map((item) => (
          <Card key={item.id} className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <p className="font-medium text-by-ink">{item.full_name}</p>
              <p className="text-xs text-by-muted">
                {item.email ?? item.phone ?? item.id} · {item.primary_role}
              </p>
            </div>
            <div className="flex gap-2">
              {item.is_seed_data ? <Badge>SEED/DEMO</Badge> : null}
              <Badge tone={item.is_active ? 'green' : 'neutral'}>
                {item.is_active ? 'active' : 'inactive'}
              </Badge>
            </div>
          </Card>
        ))}
      </ListSection>

      <ListSection
        title="Recent bookings"
        loading={bookingsQuery.isLoading}
        error={bookingsQuery.isError}
        empty={bookings.length === 0}
      >
        {bookings.map((item) => (
          <Card key={item.id} className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <p className="font-medium text-by-ink">{item.booking_number}</p>
              <p className="text-xs text-by-muted">
                {item.resource_type} · {item.status}
              </p>
            </div>
            <p className="text-sm font-medium text-by-ink">{formatInr(item.amount_inr)}</p>
          </Card>
        ))}
      </ListSection>

      <ListSection
        title="Recent payments"
        loading={paymentsQuery.isLoading}
        error={paymentsQuery.isError}
        empty={payments.length === 0}
      >
        {payments.map((item) => (
          <Card key={item.id} className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <p className="font-medium text-by-ink">{item.payment_number}</p>
              <p className="text-xs text-by-muted">
                {item.method} · {item.status}
                {item.is_mock ? ' · mock' : ''}
              </p>
            </div>
            <p className="text-sm font-medium text-by-ink">{formatInr(item.amount_inr)}</p>
          </Card>
        ))}
      </ListSection>

      <ListSection
        title="Support tickets"
        loading={ticketsQuery.isLoading}
        error={ticketsQuery.isError}
        empty={tickets.length === 0}
        emptyDescription="SOS and support tickets will appear here."
      >
        {tickets.map((item) => (
          <Card key={item.id} className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <p className="font-medium text-by-ink">{item.subject}</p>
              <p className="text-xs text-by-muted">
                {item.ticket_number} · {item.status} · {item.priority}
              </p>
            </div>
          </Card>
        ))}
      </ListSection>
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

function ListSection({
  title,
  loading,
  error,
  empty,
  emptyDescription,
  children,
}: {
  title: string
  loading: boolean
  error: boolean
  empty: boolean
  emptyDescription?: string
  children: ReactNode
}) {
  return (
    <section className="space-y-3">
      <h3 className="font-display text-lg font-semibold text-by-ink">{title}</h3>
      {loading ? <LoadingState label={`Loading ${title.toLowerCase()}…`} /> : null}
      {error ? <ErrorState title={`Could not load ${title.toLowerCase()}.`} /> : null}
      {!loading && empty ? (
        <EmptyState title={`No ${title.toLowerCase()}`} description={emptyDescription} />
      ) : null}
      <ul className="space-y-2">{children}</ul>
    </section>
  )
}
