import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States'
import { ROUTES } from '@/constants/app'
import { getWallet, listPayments, topUpWallet } from '@/services/payments'
import { useAuthStore } from '@/store/auth'

export function PaymentsPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const tokens = useAuthStore((state) => state.tokens)
  const [status, setStatus] = useState<string | undefined>()

  const walletQuery = useQuery({
    queryKey: ['wallet'],
    queryFn: async () => {
      const response = await getWallet()
      if (!response.data) throw new Error('Wallet unavailable')
      return response.data
    },
    enabled: Boolean(tokens?.access_token),
  })

  const paymentsQuery = useQuery({
    queryKey: ['payments', status ?? 'all'],
    queryFn: async () => {
      const response = await listPayments({ status })
      return response.data ?? []
    },
    enabled: Boolean(tokens?.access_token),
  })

  const topUpMutation = useMutation({
    mutationFn: async (amount: number) => topUpWallet(amount),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['wallet'] })
    },
  })

  const payments = useMemo(() => paymentsQuery.data ?? [], [paymentsQuery.data])

  if (!tokens?.access_token) {
    return (
      <Card className="space-y-4 text-left">
        <h2 className="font-display text-2xl font-semibold text-by-ink">Payments</h2>
        <p className="text-sm text-by-muted">
          Sign in to view mock payments and manage your demo wallet.
        </p>
        <Button onClick={() => navigate(ROUTES.login)}>Sign in</Button>
      </Card>
    )
  }

  return (
    <div className="flex flex-col gap-5 text-left">
      <div>
        <h2 className="font-display text-2xl font-semibold text-by-ink">Payments</h2>
        <p className="mt-1 text-sm text-by-muted">
          Mock captures only — no real money moves. Try coupon BYDEMO10 on checkout.
        </p>
      </div>

      <Card className="space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-wide text-by-muted">Demo wallet</p>
            <p className="mt-1 text-2xl font-semibold text-by-ink">
              ₹
              {Number(walletQuery.data?.balance_inr ?? 0).toLocaleString('en-IN', {
                maximumFractionDigits: 0,
              })}
            </p>
          </div>
          <Button
            size="sm"
            variant="secondary"
            disabled={topUpMutation.isPending}
            onClick={() => topUpMutation.mutate(5000)}
          >
            {topUpMutation.isPending ? 'Adding…' : 'Top up ₹5,000'}
          </Button>
        </div>
        {walletQuery.data ? (
          <p className="text-xs text-by-muted">{walletQuery.data.data_notice}</p>
        ) : null}
      </Card>

      <div className="flex flex-wrap gap-2">
        {[
          { id: 'all', label: 'All', value: undefined },
          { id: 'captured', label: 'Captured', value: 'captured' },
          { id: 'refunded', label: 'Refunded', value: 'refunded' },
        ].map((item) => (
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

      {paymentsQuery.isLoading ? <LoadingState label="Loading payments…" /> : null}
      {paymentsQuery.isError ? (
        <ErrorState
          title="Could not load payments"
          actionLabel="Retry"
          onAction={() => void paymentsQuery.refetch()}
        />
      ) : null}

      {!paymentsQuery.isLoading && payments.length === 0 ? (
        <Card>
          <EmptyState
            title="No payments yet"
            description="Open a booking and pay with mock UPI, card, or wallet."
            actionLabel="My bookings"
            onAction={() => navigate(ROUTES.bookings)}
          />
        </Card>
      ) : null}

      {payments.length > 0 ? (
        <ul className="space-y-3">
          {payments.map((payment) => (
            <li key={payment.id}>
              <Link
                to={`/payments/${payment.id}`}
                className="block rounded-[1.25rem] border border-by-border bg-white p-4 shadow-[var(--shadow-by-card)] transition hover:border-by-saffron/40"
              >
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <p className="font-semibold text-by-ink">{payment.payment_number}</p>
                    <p className="mt-1 text-xs text-by-muted">
                      {payment.method}
                      {payment.booking_number ? ` · ${payment.booking_number}` : ''}
                      {payment.coupon_code ? ` · ${payment.coupon_code}` : ''}
                    </p>
                  </div>
                  <div className="text-right">
                    <Badge
                      tone={
                        payment.status === 'refunded'
                          ? 'neutral'
                          : payment.status === 'captured'
                            ? 'green'
                            : 'blue'
                      }
                    >
                      {payment.status}
                    </Badge>
                    <p className="mt-2 text-sm font-medium text-by-ink">
                      ₹{payment.amount_inr.toLocaleString('en-IN')}
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
