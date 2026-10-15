import { Link, useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { ErrorState, LoadingState } from '@/components/feedback/States'
import { ROUTES } from '@/constants/app'
import { getPayment, refundPayment } from '@/services/payments'
import { useAuthStore } from '@/store/auth'

export function PaymentDetailsPage() {
  const { paymentId = '' } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const tokens = useAuthStore((state) => state.tokens)

  const query = useQuery({
    queryKey: ['payment', paymentId],
    queryFn: async () => {
      const response = await getPayment(paymentId)
      if (!response.data) throw new Error('Payment not found')
      return response.data
    },
    enabled: Boolean(paymentId && tokens?.access_token),
  })

  const refundMutation = useMutation({
    mutationFn: async () => refundPayment(paymentId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['payment', paymentId] })
      await queryClient.invalidateQueries({ queryKey: ['payments'] })
      await queryClient.invalidateQueries({ queryKey: ['wallet'] })
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

  if (query.isLoading) return <LoadingState label="Loading payment…" />
  if (query.isError || !query.data) {
    return (
      <ErrorState
        title="Payment not found"
        actionLabel="Payments"
        onAction={() => navigate(ROUTES.payments)}
      />
    )
  }

  const payment = query.data
  const canRefund = payment.status === 'captured'

  return (
    <div className="flex flex-col gap-5 text-left">
      <section className="overflow-hidden rounded-[1.25rem] bg-gradient-to-br from-by-blue to-by-green-dark text-white shadow-[var(--shadow-by-card)]">
        <div className="space-y-3 p-5">
          <div className="flex flex-wrap gap-2">
            {payment.is_mock ? <Badge tone="neutral">Mock</Badge> : null}
            <Badge tone="green">{payment.status}</Badge>
            <Badge tone="blue">{payment.method}</Badge>
          </div>
          <h1 className="font-display text-3xl font-semibold leading-tight">
            ₹{payment.amount_inr.toLocaleString('en-IN')}
          </h1>
          <p className="text-sm text-white/90">{payment.payment_number}</p>
        </div>
      </section>

      <Card>
        <p className="text-sm text-by-muted">{payment.data_notice}</p>
      </Card>

      <Card className="space-y-3">
        <h2 className="text-lg font-semibold text-by-ink">Details</h2>
        <dl className="grid gap-3 sm:grid-cols-2">
          <InfoItem label="Provider" value={payment.provider} />
          <InfoItem label="Reference" value={payment.provider_reference ?? '—'} />
          <InfoItem label="Booking" value={payment.booking_number ?? '—'} />
          <InfoItem label="Coupon" value={payment.coupon_code ?? 'None'} />
          <InfoItem
            label="Paid at"
            value={payment.paid_at ? new Date(payment.paid_at).toLocaleString() : '—'}
          />
          {payment.failure_reason ? (
            <InfoItem label="Failure" value={payment.failure_reason} />
          ) : null}
        </dl>
        <div className="flex flex-wrap gap-2 pt-2">
          {payment.booking_id ? (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => navigate(`/bookings/${payment.booking_id}`)}
            >
              View booking
            </Button>
          ) : null}
          {canRefund ? (
            <Button
              size="sm"
              variant="secondary"
              disabled={refundMutation.isPending}
              onClick={() => refundMutation.mutate()}
            >
              {refundMutation.isPending ? 'Refunding…' : 'Refund (mock)'}
            </Button>
          ) : null}
        </div>
      </Card>

      <div className="flex gap-3 text-sm">
        <Link to={ROUTES.payments} className="font-medium text-by-green hover:underline">
          ← Payments
        </Link>
        <Link to={ROUTES.bookings} className="font-medium text-by-blue hover:underline">
          Bookings
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
