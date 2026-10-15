import { Link, useNavigate, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { MapPinned } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { Rating } from '@/components/ui/Rating'
import { ErrorState, LoadingState } from '@/components/feedback/States'
import { MapCanvas } from '@/features/maps/MapCanvas'
import { MockBookButton } from '@/features/bookings/MockBookButton'
import { ReviewsSection } from '@/features/reviews/ReviewsSection'
import { ROUTES } from '@/constants/app'
import { getGuide } from '@/services/guides'

export function GuideDetailsPage() {
  const { guideId = '' } = useParams()
  const navigate = useNavigate()

  const query = useQuery({
    queryKey: ['guide', guideId],
    queryFn: async () => {
      const response = await getGuide(guideId)
      if (!response.data) throw new Error('Guide not found')
      return response.data
    },
    enabled: Boolean(guideId),
  })

  if (query.isLoading) return <LoadingState label="Loading guide…" />
  if (query.isError || !query.data) {
    return (
      <ErrorState
        title="Guide not found"
        description="This profile may be unavailable. Try Local guides."
        actionLabel="Browse guides"
        onAction={() => navigate(ROUTES.guides)}
      />
    )
  }

  const guide = query.data
  const hasCoords = guide.latitude != null && guide.longitude != null

  return (
    <div className="flex flex-col gap-5 text-left">
      <section className="overflow-hidden rounded-[1.25rem] bg-gradient-to-br from-by-green-dark to-by-blue text-white shadow-[var(--shadow-by-card)]">
        <div className="space-y-3 p-5">
          <div className="flex flex-wrap gap-2">
            {guide.is_seed_data ? <Badge tone="neutral">Demo data</Badge> : null}
            {guide.specialization ? <Badge tone="green">{guide.specialization}</Badge> : null}
          </div>
          <h1 className="font-display text-3xl font-semibold leading-tight">
            {guide.display_name}
          </h1>
          <p className="flex items-center gap-1 text-sm text-white/90">
            <MapPinned className="size-4" aria-hidden />
            {guide.city_name}, {guide.state_name}
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <Rating value={Number(guide.rating_avg)} className="text-white" />
            <span className="text-sm text-white/85">{guide.rating_count} reviews</span>
            <span className="text-sm font-medium">
              ₹{guide.price_per_day_inr.toLocaleString('en-IN')}/day
            </span>
          </div>
        </div>
      </section>

      <Card>
        <p className="text-sm text-by-muted">{guide.data_notice}</p>
      </Card>

      <Card className="space-y-3">
        <h2 className="text-lg font-semibold text-by-ink">About</h2>
        <p className="text-sm leading-relaxed text-by-muted">
          {guide.bio ?? 'No bio available yet.'}
        </p>
        <dl className="grid gap-3 sm:grid-cols-2">
          <InfoItem label="Languages" value={guide.languages} />
          <InfoItem
            label="Experience"
            value={`${guide.experience_years} year${guide.experience_years === 1 ? '' : 's'}`}
          />
          <InfoItem label="Specialization" value={guide.specialization} />
        </dl>
      </Card>

      <Card className="space-y-3">
        <h2 className="text-lg font-semibold text-by-ink">Upcoming availability (demo)</h2>
        {guide.availability.length === 0 ? (
          <p className="text-sm text-by-muted">No upcoming dates listed yet.</p>
        ) : (
          <ul className="flex flex-wrap gap-2">
            {guide.availability.map((slot) => (
              <li key={slot.id}>
                <Badge tone={slot.is_available ? 'green' : 'neutral'}>
                  {slot.available_date}
                </Badge>
              </li>
            ))}
          </ul>
        )}
        <MockBookButton
          resourceType="guide"
          resourceId={guide.id}
          label="Book guide (mock)"
          extras={{ duration_days: 1 }}
        />
      </Card>

      {hasCoords ? (
        <Card className="space-y-3">
          <h2 className="text-lg font-semibold text-by-ink">Based in</h2>
          <MapCanvas
            center={{ lat: Number(guide.latitude), lng: Number(guide.longitude) }}
            zoom={12}
            markers={[
              {
                id: guide.id,
                position: {
                  lat: Number(guide.latitude),
                  lng: Number(guide.longitude),
                },
                title: guide.display_name,
                subtitle: guide.city_name,
                tone: 'green',
              },
            ]}
          />
        </Card>
      ) : null}

      <ReviewsSection targetType="guide" targetId={guide.id} />

      <div className="flex gap-3 text-sm">
        <Link to={ROUTES.guides} className="font-medium text-by-green hover:underline">
          ← Guides
        </Link>
        <Link to={ROUTES.restaurants} className="font-medium text-by-blue hover:underline">
          Restaurants
        </Link>
      </div>
    </div>
  )
}

function InfoItem({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-by-muted">{label}</dt>
      <dd className="mt-1 text-sm text-by-ink">{value || 'Not available'}</dd>
    </div>
  )
}
