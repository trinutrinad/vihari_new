import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { ErrorState, LoadingState } from '@/components/feedback/States'
import { ROUTES } from '@/constants/app'
import { cancelBooking, getBooking } from '@/services/bookings'
import { createPayment, listPayments } from '@/services/payments'
import { useAuthStore } from '@/store/auth'
import type { PaymentMethod } from '@/types/payments'

const PAY_METHODS: Array<{ id: PaymentMethod; label: string }> = [
  { id: 'upi', label: 'UPI' },
  { id: 'card', label: 'Card' },
  { id: 'wallet', label: 'Wallet' },
  { id: 'mock', label: 'Mock' },
]

export function BookingDetailsPage() {
  const { bookingId = '' } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const tokens = useAuthStore((state) => state.tokens)
  const [method, setMethod] = useState<PaymentMethod>('upi')
  const [coupon, setCoupon] = useState('BYDEMO10')
  const [payError, setPayError] = useState<string | null>(null)

  const query = useQuery({
    queryKey: ['booking', bookingId],
    queryFn: async () => {
      const response = await getBooking(bookingId)
      if (!response.data) throw new Error('Booking not found')
      return response.data
    },
    enabled: Boolean(bookingId && tokens?.access_token),
  })

  const paymentsQuery = useQuery({
    queryKey: ['payments', 'booking', bookingId],
    queryFn: async () => {
      const response = await listPayments({ booking_id: bookingId })
      return response.data ?? []
    },
    enabled: Boolean(bookingId && tokens?.access_token),
  })

  const cancelMutation = useMutation({
    mutationFn: async () => cancelBooking(bookingId, 'Cancelled from app (mock)'),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['booking', bookingId] })
      await queryClient.invalidateQueries({ queryKey: ['bookings'] })
    },
  })

  const payMutation = useMutation({
    mutationFn: async () =>
      createPayment({
        booking_id: bookingId,
        method,
        coupon_code: coupon.trim() || undefined,
      }),
    onSuccess: async (response) => {
      setPayError(null)
      await queryClient.invalidateQueries({ queryKey: ['payments'] })
      await queryClient.invalidateQueries({ queryKey: ['wallet'] })
      if (response.data?.id) navigate(`/payments/${response.data.id}`)
    },
    onError: (error: Error) => {
      setPayError(error.message || 'Payment failed')
    },
  })

  if (!tokens?.access_token) {
    return (
      <Card className="space-y-3 text-left">
        <h2 className="text-lg font-semibold text-by-ink">Sign in required</h2>
        <Button onClick={() => navigate(ROUTES.login)}>Sign in</Button>
      </Card>
    )
  }

  if (query.isLoading) return <LoadingState label="Loading booking…" />
  if (query.isError || !query.data) {
    return (
      <ErrorState
        title="Booking not found"
        description="This booking may belong to another account."
        actionLabel="My bookings"
        onAction={() => navigate(ROUTES.bookings)}
      />
    )
  }

  const booking = query.data
  const canCancel = booking.status !== 'cancelled' && booking.status !== 'completed'
  const captured = (paymentsQuery.data ?? []).find((item) => item.status === 'captured')
  const canPay =
    booking.status !== 'cancelled' && !captured && !payMutation.isPending

  return (
    <div className="flex flex-col gap-5 text-left">
      <section className="overflow-hidden rounded-[1.25rem] bg-gradient-to-br from-by-green-dark to-by-blue text-white shadow-[var(--shadow-by-card)]">
        <div className="space-y-3 p-5">
          <div className="flex flex-wrap gap-2">
            {booking.is_mock ? <Badge tone="neutral">Mock</Badge> : null}
            <Badge tone="green">{booking.status}</Badge>
            <Badge tone="blue">{booking.resource_type}</Badge>
          </div>
          <h1 className="font-display text-3xl font-semibold leading-tight">
            {booking.resource_title}
          </h1>
          <p className="text-sm text-white/90">{booking.booking_number}</p>
        </div>
      </section>

      <Card>
        <p className="text-sm text-by-muted">{booking.data_notice}</p>
      </Card>

      <Card className="space-y-3">
        <h2 className="text-lg font-semibold text-by-ink">Details</h2>
        <dl className="grid gap-3 sm:grid-cols-2">
          <InfoItem
            label="Amount"
            value={`₹${booking.amount_inr.toLocaleString('en-IN')} ${booking.currency}`}
          />
          <InfoItem label="Provider" value={booking.provider ?? 'mock'} />
          <InfoItem
            label="Scheduled"
            value={
              booking.scheduled_at
                ? new Date(booking.scheduled_at).toLocaleString()
                : 'Not set'
            }
          />
          <InfoItem label="Location" value={booking.location_text ?? '—'} />
          {booking.cancellation_reason ? (
            <InfoItem label="Cancellation" value={booking.cancellation_reason} />
          ) : null}
          {booking.notes ? <InfoItem label="Notes" value={booking.notes} /> : null}
        </dl>
        <div className="flex flex-wrap gap-2 pt-2">
          {booking.resource_href ? (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => navigate(booking.resource_href!)}
            >
              View resource
            </Button>
          ) : null}
          {canCancel ? (
            <Button
              size="sm"
              variant="secondary"
              disabled={cancelMutation.isPending}
              onClick={() => cancelMutation.mutate()}
            >
              {cancelMutation.isPending ? 'Cancelling…' : 'Cancel booking'}
            </Button>
          ) : null}
        </div>
      </Card>

      <Card className="space-y-3">
        <h2 className="text-lg font-semibold text-by-ink">Payment (mock)</h2>
        {captured ? (
          <div className="space-y-2">
            <p className="text-sm text-by-muted">
              Paid ₹{captured.amount_inr.toLocaleString('en-IN')} via {captured.method}.
            </p>
            <Button size="sm" onClick={() => navigate(`/payments/${captured.id}`)}>
              View payment
            </Button>
          </div>
        ) : (
          <>
            <div className="flex flex-wrap gap-2">
              {PAY_METHODS.map((item) => (
                <Button
                  key={item.id}
                  size="sm"
                  variant={method === item.id ? 'primary' : 'ghost'}
                  onClick={() => setMethod(item.id)}
                >
                  {item.label}
                </Button>
              ))}
            </div>
            <label className="block text-sm text-by-muted" htmlFor="coupon-code">
              Coupon (optional)
            </label>
            <input
              id="coupon-code"
              value={coupon}
              onChange={(event) => setCoupon(event.target.value.toUpperCase())}
              className="w-full max-w-xs rounded-xl border border-by-border bg-white px-3 py-2 text-sm text-by-ink outline-none focus:border-by-green"
              placeholder="BYDEMO10"
            />
            <Button
              size="sm"
              variant="secondary"
              disabled={!canPay}
              onClick={() => payMutation.mutate()}
            >
              {payMutation.isPending ? 'Paying…' : 'Pay now (mock)'}
            </Button>
            {payError ? <p className="text-xs text-red-600">{payError}</p> : null}
          </>
        )}
      </Card>

      <div className="flex gap-3 text-sm">
        <Link to={ROUTES.bookings} className="font-medium text-by-green hover:underline">
          ← Bookings
        </Link>
        <Link to={ROUTES.payments} className="font-medium text-by-blue hover:underline">
          Payments
        </Link>
      </div>
    </div>
  )
}

function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-by-muted">{label}</dt>
      <dd className="mt-1 text-sm text-by-ink">{value}</dd>
    </div>
  )
}
