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
import { getRestaurant, getRestaurantBySlug } from '@/services/restaurants'

export function RestaurantDetailsPage() {
  const { restaurantId = '', slug = '' } = useParams()
  const navigate = useNavigate()

  const query = useQuery({
    queryKey: ['restaurant', restaurantId || slug],
    queryFn: async () => {
      if (slug) {
        const response = await getRestaurantBySlug(slug)
        if (!response.data) throw new Error('Restaurant not found')
        return response.data
      }
      const response = await getRestaurant(restaurantId)
      if (!response.data) throw new Error('Restaurant not found')
      return response.data
    },
    enabled: Boolean(restaurantId || slug),
  })

  if (query.isLoading) return <LoadingState label="Loading restaurant…" />
  if (query.isError || !query.data) {
    return (
      <ErrorState
        title="Restaurant not found"
        description="This place may be unavailable. Try Restaurants."
        actionLabel="Browse restaurants"
        onAction={() => navigate(ROUTES.restaurants)}
      />
    )
  }

  const restaurant = query.data
  const hasCoords = restaurant.latitude != null && restaurant.longitude != null

  return (
    <div className="flex flex-col gap-5 text-left">
      <section className="overflow-hidden rounded-[1.25rem] bg-gradient-to-br from-by-saffron to-by-green-dark text-white shadow-[var(--shadow-by-card)]">
        <div className="space-y-3 p-5">
          <div className="flex flex-wrap gap-2">
            {restaurant.is_seed_data ? <Badge tone="neutral">Demo data</Badge> : null}
            {restaurant.cuisine_tags ? <Badge tone="blue">{restaurant.cuisine_tags}</Badge> : null}
            {restaurant.is_vegetarian ? <Badge tone="green">Vegetarian</Badge> : null}
          </div>
          <h1 className="font-display text-3xl font-semibold leading-tight">
            {restaurant.name}
          </h1>
          <p className="flex items-center gap-1 text-sm text-white/90">
            <MapPinned className="size-4" aria-hidden />
            {restaurant.city_name}, {restaurant.state_name}
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <Rating value={Number(restaurant.rating_avg)} className="text-white" />
            <span className="text-sm text-white/85">{restaurant.rating_count} reviews</span>
            <span className="text-sm font-medium">
              {'₹'.repeat(Math.min(Math.max(restaurant.price_level, 1), 4))}
            </span>
          </div>
        </div>
      </section>

      <Card>
        <p className="text-sm text-by-muted">{restaurant.data_notice}</p>
      </Card>

      <Card className="space-y-3">
        <h2 className="text-lg font-semibold text-by-ink">About</h2>
        <p className="text-sm leading-relaxed text-by-muted">
          {restaurant.description ?? 'No description available yet.'}
        </p>
        <dl className="grid gap-3 sm:grid-cols-2">
          <InfoItem label="Address" value={restaurant.address} />
          <InfoItem label="Hours" value={restaurant.opening_hours} />
        </dl>
      </Card>

      <Card className="space-y-3">
        <h2 className="text-lg font-semibold text-by-ink">Menu (demo)</h2>
        {restaurant.menu_items.length === 0 ? (
          <p className="text-sm text-by-muted">No menu items listed yet.</p>
        ) : (
          <ul className="space-y-2">
            {restaurant.menu_items.map((item) => (
              <li
                key={item.id}
                className="flex flex-wrap items-center justify-between gap-2 rounded-xl bg-by-saffron-soft/60 px-3 py-2"
              >
                <div>
                  <p className="text-sm font-medium text-by-ink">
                    {item.name}
                    {item.is_veg ? ' · Veg' : ' · Non-veg'}
                  </p>
                  {item.description ? (
                    <p className="text-xs text-by-muted">{item.description}</p>
                  ) : null}
                </div>
                <p className="text-sm font-semibold text-by-ink">
                  ₹{item.price_inr.toLocaleString('en-IN')}
                </p>
              </li>
            ))}
          </ul>
        )}
        <MockBookButton
          resourceType="restaurant"
          resourceId={restaurant.id}
          label="Order food (mock)"
        />
      </Card>

      {hasCoords ? (
        <Card className="space-y-3">
          <h2 className="text-lg font-semibold text-by-ink">Map</h2>
          <MapCanvas
            center={{ lat: Number(restaurant.latitude), lng: Number(restaurant.longitude) }}
            zoom={13}
            markers={[
              {
                id: restaurant.id,
                position: {
                  lat: Number(restaurant.latitude),
                  lng: Number(restaurant.longitude),
                },
                title: restaurant.name,
                subtitle: restaurant.city_name,
                tone: 'saffron',
              },
            ]}
          />
        </Card>
      ) : null}

      <ReviewsSection targetType="restaurant" targetId={restaurant.id} />

      <div className="flex gap-3 text-sm">
        <Link to={ROUTES.restaurants} className="font-medium text-by-green hover:underline">
          ← Restaurants
        </Link>
        <Link to={ROUTES.hotels} className="font-medium text-by-blue hover:underline">
          Hotels
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
