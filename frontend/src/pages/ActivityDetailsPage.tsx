import { Link, useNavigate, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Clock3, MapPinned } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { Rating } from '@/components/ui/Rating'
import { ErrorState, LoadingState } from '@/components/feedback/States'
import { MapCanvas } from '@/features/maps/MapCanvas'
import { MockBookButton } from '@/features/bookings/MockBookButton'
import { ReviewsSection } from '@/features/reviews/ReviewsSection'
import { ROUTES } from '@/constants/app'
import { getActivity, getActivityBySlug } from '@/services/activities'

export function ActivityDetailsPage() {
  const { activityId = '', slug = '' } = useParams()
  const navigate = useNavigate()

  const query = useQuery({
    queryKey: ['activity', activityId || slug],
    queryFn: async () => {
      if (slug) {
        const response = await getActivityBySlug(slug)
        if (!response.data) throw new Error('Activity not found')
        return response.data
      }
      const response = await getActivity(activityId)
      if (!response.data) throw new Error('Activity not found')
      return response.data
    },
    enabled: Boolean(activityId || slug),
  })

  if (query.isLoading) return <LoadingState label="Loading activity…" />
  if (query.isError || !query.data) {
    return (
      <ErrorState
        title="Activity not found"
        description="This experience may be unavailable. Try Activities."
        actionLabel="Browse activities"
        onAction={() => navigate(ROUTES.activities)}
      />
    )
  }

  const activity = query.data
  const hasCoords = activity.latitude != null && activity.longitude != null

  return (
    <div className="flex flex-col gap-5 text-left">
      <section className="overflow-hidden rounded-[1.25rem] bg-gradient-to-br from-by-saffron to-by-blue text-white shadow-[var(--shadow-by-card)]">
        <div className="space-y-3 p-5">
          <div className="flex flex-wrap gap-2">
            {activity.is_seed_data ? <Badge tone="neutral">Demo data</Badge> : null}
            <Badge tone="saffron">{activity.category}</Badge>
          </div>
          <h1 className="font-display text-3xl font-semibold leading-tight">
            {activity.name}
          </h1>
          <p className="flex items-center gap-1 text-sm text-white/90">
            <MapPinned className="size-4" aria-hidden />
            {activity.city_name}, {activity.state_name}
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <Rating value={Number(activity.rating_avg)} className="text-white" />
            <span className="text-sm text-white/85">{activity.rating_count} reviews</span>
            <span className="text-sm font-medium">
              ₹{activity.price_inr.toLocaleString('en-IN')}
            </span>
            {activity.duration_hours != null ? (
              <span className="inline-flex items-center gap-1 text-sm text-white/85">
                <Clock3 className="size-4" aria-hidden />
                {Number(activity.duration_hours)} hrs
              </span>
            ) : null}
          </div>
        </div>
      </section>

      <Card>
        <p className="text-sm text-by-muted">{activity.data_notice}</p>
      </Card>

      <Card className="space-y-3">
        <h2 className="text-lg font-semibold text-by-ink">About</h2>
        <p className="text-sm leading-relaxed text-by-muted">
          {activity.description ?? 'No description available yet.'}
        </p>
      </Card>

      <Card className="space-y-3">
        <h2 className="text-lg font-semibold text-by-ink">Safety (demo)</h2>
        <p className="text-sm leading-relaxed text-by-muted">
          {activity.safety_information ?? 'Confirm safety guidance with the operator.'}
        </p>
        <MockBookButton
          resourceType="activity"
          resourceId={activity.id}
          label="Book activity (mock)"
          extras={{ participants: 1 }}
        />
      </Card>

      {hasCoords ? (
        <Card className="space-y-3">
          <h2 className="text-lg font-semibold text-by-ink">Map</h2>
          <MapCanvas
            center={{ lat: Number(activity.latitude), lng: Number(activity.longitude) }}
            zoom={12}
            markers={[
              {
                id: activity.id,
                position: {
                  lat: Number(activity.latitude),
                  lng: Number(activity.longitude),
                },
                title: activity.name,
                subtitle: activity.city_name,
                tone: 'saffron',
              },
            ]}
          />
        </Card>
      ) : null}

      <ReviewsSection targetType="activity" targetId={activity.id} />

      <div className="flex gap-3 text-sm">
        <Link to={ROUTES.activities} className="font-medium text-by-green hover:underline">
          ← Activities
        </Link>
        <Link to={ROUTES.transport} className="font-medium text-by-blue hover:underline">
          Transport
        </Link>
      </div>
    </div>
  )
}
