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
import { getHotel, getHotelBySlug } from '@/services/hotels'

export function HotelDetailsPage() {
  const { hotelId = '', slug = '' } = useParams()
  const navigate = useNavigate()

  const query = useQuery({
    queryKey: ['hotel', hotelId || slug],
    queryFn: async () => {
      if (slug) {
        const response = await getHotelBySlug(slug)
        if (!response.data) throw new Error('Hotel not found')
        return response.data
      }
      const response = await getHotel(hotelId)
      if (!response.data) throw new Error('Hotel not found')
      return response.data
    },
    enabled: Boolean(hotelId || slug),
  })

  if (query.isLoading) return <LoadingState label="Loading hotel…" />
  if (query.isError || !query.data) {
    return (
      <ErrorState
        title="Hotel not found"
        description="This stay may be unavailable. Try Hotels."
        actionLabel="Browse hotels"
        onAction={() => navigate(ROUTES.hotels)}
      />
    )
  }

  const hotel = query.data
  const hasCoords = hotel.latitude != null && hotel.longitude != null

  return (
    <div className="flex flex-col gap-5 text-left">
      <section className="overflow-hidden rounded-[1.25rem] bg-gradient-to-br from-by-blue to-by-green-dark text-white shadow-[var(--shadow-by-card)]">
        <div className="space-y-3 p-5">
          <div className="flex flex-wrap gap-2">
            {hotel.is_seed_data ? <Badge tone="neutral">Demo data</Badge> : null}
            <Badge tone="blue">{hotel.provenance}</Badge>
          </div>
          <h1 className="font-display text-3xl font-semibold leading-tight">{hotel.name}</h1>
          <p className="flex items-center gap-1 text-sm text-white/90">
            <MapPinned className="size-4" aria-hidden />
            {hotel.city_name}, {hotel.state_name}
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <Rating value={Number(hotel.rating_avg)} className="text-white" />
            <span className="text-sm text-white/85">{hotel.rating_count} reviews</span>
            {hotel.starting_price_inr != null ? (
              <span className="text-sm font-medium">
                from ₹{hotel.starting_price_inr.toLocaleString('en-IN')} / night
              </span>
            ) : null}
          </div>
          <div className="flex flex-wrap gap-2 pt-1">
            {hotel.has_wifi ? <Badge tone="green">Wi‑Fi</Badge> : null}
            {hotel.has_ac ? <Badge tone="green">AC</Badge> : null}
            {hotel.has_breakfast ? <Badge tone="saffron">Breakfast</Badge> : null}
            {hotel.has_parking ? <Badge tone="neutral">Parking</Badge> : null}
            {hotel.has_pool ? <Badge tone="blue">Pool</Badge> : null}
          </div>
        </div>
      </section>

      <Card>
        <p className="text-sm text-by-muted">{hotel.data_notice}</p>
      </Card>

      <Card className="space-y-3">
        <h2 className="text-lg font-semibold text-by-ink">About</h2>
        <p className="text-sm leading-relaxed text-by-muted">
          {hotel.description ?? 'No description available yet.'}
        </p>
        <dl className="grid gap-3 sm:grid-cols-2">
          <InfoItem label="Address" value={hotel.address} />
          <InfoItem label="Cancellation" value={hotel.cancellation_policy} />
        </dl>
      </Card>

      <Card className="space-y-3">
        <h2 className="text-lg font-semibold text-by-ink">Rooms</h2>
        {hotel.rooms.length === 0 ? (
          <p className="text-sm text-by-muted">No rooms listed yet.</p>
        ) : (
          <ul className="space-y-2">
            {hotel.rooms.map((room) => (
              <li
                key={room.id}
                className="flex flex-wrap items-center justify-between gap-2 rounded-xl bg-by-green-soft/60 px-3 py-2"
              >
                <div>
                  <p className="text-sm font-medium text-by-ink">{room.name}</p>
                  <p className="text-xs text-by-muted">
                    Up to {room.max_guests} guests · {room.total_rooms} rooms
                    {room.is_available ? '' : ' · Unavailable'}
                  </p>
                </div>
                <p className="text-sm font-semibold text-by-ink">
                  ₹{room.price_per_night_inr.toLocaleString('en-IN')}/night
                </p>
              </li>
            ))}
          </ul>
        )}
        <MockBookButton
          resourceType="hotel"
          resourceId={hotel.id}
          label="Book stay (mock)"
          extras={{ nights: 1 }}
        />
      </Card>

      {hasCoords ? (
        <Card className="space-y-3">
          <h2 className="text-lg font-semibold text-by-ink">Map</h2>
          <MapCanvas
            center={{ lat: Number(hotel.latitude), lng: Number(hotel.longitude) }}
            zoom={13}
            markers={[
              {
                id: hotel.id,
                position: { lat: Number(hotel.latitude), lng: Number(hotel.longitude) },
                title: hotel.name,
                subtitle: hotel.city_name,
                tone: 'blue',
              },
            ]}
          />
        </Card>
      ) : null}

      <ReviewsSection targetType="hotel" targetId={hotel.id} />

      <div className="flex gap-3 text-sm">
        <Link to={ROUTES.hotels} className="font-medium text-by-green hover:underline">
          ← Hotels
        </Link>
        <Link to={ROUTES.explore} className="font-medium text-by-blue hover:underline">
          Explore places
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
