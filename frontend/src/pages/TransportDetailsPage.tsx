import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { ErrorState, LoadingState } from '@/components/feedback/States'
import { ROUTES } from '@/constants/app'
import { MockBookButton } from '@/features/bookings/MockBookButton'
import { estimateTransportFare, getTransportByCode, getTransportOption } from '@/services/transport'

export function TransportDetailsPage() {
  const { optionId = '', code = '' } = useParams()
  const navigate = useNavigate()
  const [distanceKm, setDistanceKm] = useState('10')

  const query = useQuery({
    queryKey: ['transport-option', optionId || code],
    queryFn: async () => {
      if (code) {
        const response = await getTransportByCode(code)
        if (!response.data) throw new Error('Transport option not found')
        return response.data
      }
      const response = await getTransportOption(optionId)
      if (!response.data) throw new Error('Transport option not found')
      return response.data
    },
    enabled: Boolean(optionId || code),
  })

  const distance = Number(distanceKm)
  const estimateQuery = useQuery({
    queryKey: ['transport-estimate', query.data?.id, distance],
    queryFn: async () => {
      const response = await estimateTransportFare({
        option_id: query.data!.id,
        distance_km: distance,
      })
      if (!response.data) throw new Error('Estimate failed')
      return response.data
    },
    enabled: Boolean(query.data?.id) && Number.isFinite(distance) && distance > 0,
  })

  if (query.isLoading) return <LoadingState label="Loading transport…" />
  if (query.isError || !query.data) {
    return (
      <ErrorState
        title="Transport option not found"
        description="This option may be unavailable. Try Transport."
        actionLabel="Browse transport"
        onAction={() => navigate(ROUTES.transport)}
      />
    )
  }

  const option = query.data

  return (
    <div className="flex flex-col gap-5 text-left">
      <section className="overflow-hidden rounded-[1.25rem] bg-gradient-to-br from-by-blue to-by-green-dark text-white shadow-[var(--shadow-by-card)]">
        <div className="space-y-3 p-5">
          <div className="flex flex-wrap gap-2">
            {option.is_seed_data ? <Badge tone="neutral">Demo data</Badge> : null}
            <Badge tone="blue">{option.vehicle_type.replaceAll('_', ' ')}</Badge>
          </div>
          <h1 className="font-display text-3xl font-semibold leading-tight">{option.name}</h1>
          <p className="text-sm text-white/90">Code: {option.code}</p>
        </div>
      </section>

      <Card>
        <p className="text-sm text-by-muted">{option.data_notice}</p>
      </Card>

      <Card className="space-y-3">
        <h2 className="text-lg font-semibold text-by-ink">About</h2>
        <p className="text-sm leading-relaxed text-by-muted">
          {option.description ?? 'No description available yet.'}
        </p>
        <dl className="grid gap-3 sm:grid-cols-2">
          <InfoItem
            label="Base fare"
            value={`₹${option.base_fare_inr.toLocaleString('en-IN')}`}
          />
          <InfoItem
            label="Per km"
            value={
              option.per_km_inr > 0
                ? `₹${option.per_km_inr.toLocaleString('en-IN')}`
                : 'Not fixed'
            }
          />
        </dl>
      </Card>

      <Card className="space-y-3">
        <h2 className="text-lg font-semibold text-by-ink">Fare estimate (demo)</h2>
        <label className="block text-sm text-by-muted" htmlFor="distance-km">
          Distance (km)
        </label>
        <input
          id="distance-km"
          type="number"
          min={1}
          max={2000}
          step={1}
          value={distanceKm}
          onChange={(event) => setDistanceKm(event.target.value)}
          className="w-full max-w-xs rounded-xl border border-by-border bg-white px-3 py-2 text-sm text-by-ink outline-none focus:border-by-green"
        />
        {estimateQuery.data ? (
          <p className="text-lg font-semibold text-by-ink">
            {estimateQuery.data.estimated_fare_inr != null
              ? `≈ ₹${estimateQuery.data.estimated_fare_inr.toLocaleString('en-IN')}`
              : 'Fare varies by route / operator'}
          </p>
        ) : null}
        {estimateQuery.data ? (
          <p className="text-xs text-by-muted">{estimateQuery.data.note}</p>
        ) : null}
        <MockBookButton
          resourceType="transport"
          resourceId={option.id}
          label="Book ride (mock)"
          extras={{
            distance_km: Number.isFinite(distance) && distance > 0 ? distance : 10,
          }}
        />
      </Card>

      <div className="flex gap-3 text-sm">
        <Link to={ROUTES.transport} className="font-medium text-by-green hover:underline">
          ← Transport
        </Link>
        <Link to={ROUTES.guides} className="font-medium text-by-blue hover:underline">
          Guides
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
