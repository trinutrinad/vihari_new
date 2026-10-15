import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import {
  Bookmark,
  BookmarkCheck,
  MapPinned,
  Navigation,
  Share2,
} from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Rating } from '@/components/ui/Rating'
import { PlaceCard } from '@/components/ui/PlaceCard'
import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States'
import { MapCanvas } from '@/features/maps/MapCanvas'
import type { MapMarkerModel } from '@/features/maps/mapProvider'
import { ReviewsSection } from '@/features/reviews/ReviewsSection'
import { ROUTES } from '@/constants/app'
import { getPlace, getPlaceBySlug, savePlace, unsavePlace } from '@/services/places'
import { useAuthStore } from '@/store/auth'
import { apiPlaceToCard } from '@/utils/placeCards'

export function PlaceDetailsPage() {
  const { placeId = '', slug = '' } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const tokens = useAuthStore((state) => state.tokens)

  const query = useQuery({
    queryKey: ['place', placeId || slug],
    queryFn: async () => {
      if (slug) {
        const response = await getPlaceBySlug(slug)
        if (!response.data) throw new Error('Place not found')
        return response.data
      }
      const response = await getPlace(placeId)
      if (!response.data) throw new Error('Place not found')
      return response.data
    },
    enabled: Boolean(placeId || slug),
  })

  const saveMutation = useMutation({
    mutationFn: async (saved: boolean) => {
      if (!query.data) return
      if (saved) await unsavePlace(query.data.id)
      else await savePlace(query.data.id)
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['place', placeId || slug] })
    },
  })

  if (query.isLoading) return <LoadingState label="Loading place…" />
  if (query.isError || !query.data) {
    return (
      <ErrorState
        title="Place not found"
        description="This destination may be unavailable. Try Explore."
        actionLabel="Explore places"
        onAction={() => navigate(ROUTES.explore)}
      />
    )
  }

  const place = query.data
  const hasCoords = place.latitude != null && place.longitude != null
  const mapsUrl = hasCoords
      ? `https://www.openstreetmap.org/?mlat=${place.latitude}&mlon=${place.longitude}#map=14/${place.latitude}/${place.longitude}`
      : null

  const mapMarkers: MapMarkerModel[] = []
  if (hasCoords) {
    mapMarkers.push({
      id: place.id,
      position: { lat: Number(place.latitude), lng: Number(place.longitude) },
      title: place.name,
      subtitle: `${place.city_name}, ${place.state_name}`,
      tone: 'saffron',
      href: `/places/${place.id}`,
    })
    for (const nearby of place.nearby_places) {
      if (nearby.latitude == null || nearby.longitude == null) continue
      mapMarkers.push({
        id: nearby.id,
        position: { lat: Number(nearby.latitude), lng: Number(nearby.longitude) },
        title: nearby.name,
        subtitle: nearby.city_name,
        tone: 'green',
        href: `/places/${nearby.id}`,
      })
    }
  }

  async function onShare() {
    const url = window.location.href
    if (navigator.share) {
      await navigator.share({ title: place.name, url })
      return
    }
    await navigator.clipboard.writeText(url)
  }

  return (
    <div className="flex flex-col gap-5 text-left">
      <section className="overflow-hidden rounded-[1.25rem] bg-gradient-to-br from-by-green to-by-green-dark text-white shadow-[var(--shadow-by-card)]">
        <div className="space-y-3 p-5">
          <div className="flex flex-wrap gap-2">
            {place.category ? <Badge tone="saffron">{place.category.name}</Badge> : null}
            {place.is_seed_data ? <Badge tone="neutral">Demo data</Badge> : null}
            <Badge tone="blue">{place.provenance}</Badge>
          </div>
          <h1 className="font-display text-3xl font-semibold leading-tight">{place.name}</h1>
          <p className="flex items-center gap-1 text-sm text-white/90">
            <MapPinned className="size-4" aria-hidden />
            {place.city_name}, {place.state_name}
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <Rating value={Number(place.rating_avg)} className="text-white" />
            <span className="text-sm text-white/85">{place.rating_count} reviews</span>
            {place.estimated_cost_inr != null ? (
              <span className="text-sm font-medium">
                ~₹{place.estimated_cost_inr.toLocaleString('en-IN')} est.
              </span>
            ) : null}
          </div>
          <div className="flex flex-wrap gap-2 pt-1">
            <Button
              size="sm"
              variant="saffron"
              leftIcon={place.is_saved ? <BookmarkCheck className="size-4" /> : <Bookmark className="size-4" />}
              onClick={() => {
                if (!tokens?.access_token) {
                  navigate(ROUTES.login)
                  return
                }
                saveMutation.mutate(place.is_saved)
              }}
            >
              {place.is_saved ? 'Saved' : 'Save'}
            </Button>
            <Button size="sm" variant="ghost" className="bg-white/10 text-white" onClick={() => void onShare()} leftIcon={<Share2 className="size-4" />}>
              Share
            </Button>
            {mapsUrl ? (
              <a href={mapsUrl} target="_blank" rel="noreferrer">
                <Button size="sm" variant="secondary" leftIcon={<Navigation className="size-4" />}>
                  Navigate
                </Button>
              </a>
            ) : null}
          </div>
        </div>
      </section>

      <Card>
        <p className="text-sm text-by-muted">{place.data_notice}</p>
      </Card>

      <Card className="space-y-3">
        <h2 className="text-lg font-semibold text-by-ink">About</h2>
        <p className="text-sm leading-relaxed text-by-muted">
          {place.description ?? place.short_description ?? 'No description available yet.'}
        </p>
        <dl className="grid gap-3 sm:grid-cols-2">
          <InfoItem label="Best time to visit" value={place.best_time_to_visit} />
          <InfoItem
            label="Opening hours"
            value={place.opening_hours ?? 'Not verified — confirm locally'}
          />
          <InfoItem label="Entry fee" value={place.entry_fee_notes} />
          <InfoItem label="How to reach" value={place.how_to_reach} />
          <InfoItem label="Facilities" value={place.facilities} />
          <InfoItem label="Address" value={place.address} />
        </dl>
      </Card>

      {hasCoords ? (
        <Card className="space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 className="text-lg font-semibold text-by-ink">Map</h2>
            <Link to={`${ROUTES.map}?city=india`} className="text-sm font-medium text-by-blue hover:underline">
              Open explore map
            </Link>
          </div>
          <MapCanvas
            center={{ lat: Number(place.latitude), lng: Number(place.longitude) }}
            zoom={12}
            markers={mapMarkers}
            fitMarkers={mapMarkers.length > 1}
            onMarkerSelect={(marker) => {
              if (marker.href && marker.id !== place.id) navigate(marker.href)
            }}
          />
          {mapsUrl ? (
            <a
              className="inline-flex text-sm font-medium text-by-blue hover:underline"
              href={mapsUrl}
              target="_blank"
              rel="noreferrer"
            >
              Open in OpenStreetMap
            </a>
          ) : null}
        </Card>
      ) : null}

      <ReviewsSection targetType="place" targetId={place.id} />

      <NearbyList title="Nearby places" empty="No nearby places yet.">
        {place.nearby_places.map((item) => (
          <PlaceCard
            key={item.id}
            place={apiPlaceToCard(item)}
            onSelect={() => navigate(`/places/${item.id}`)}
          />
        ))}
      </NearbyList>

      <Card className="space-y-2">
        <h2 className="text-lg font-semibold text-by-ink">Nearby hotels</h2>
        {place.nearby_hotels.length === 0 ? (
          <p className="text-sm text-by-muted">No hotels linked yet.</p>
        ) : (
          <ul className="space-y-2">
            {place.nearby_hotels.map((hotel) => (
              <li key={hotel.id}>
                <Link
                  to={`/hotels/${hotel.id}`}
                  className="block rounded-xl bg-by-green-soft px-3 py-2 text-sm hover:bg-by-green-soft/80"
                >
                  <span className="font-medium text-by-ink">{hotel.name}</span>
                  {hotel.starting_price_inr != null
                    ? ` · from ₹${hotel.starting_price_inr.toLocaleString('en-IN')}`
                    : ''}
                  {hotel.is_seed_data ? ' · Demo' : ''}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card className="space-y-2">
        <h2 className="text-lg font-semibold text-by-ink">Nearby restaurants</h2>
        {place.nearby_restaurants.length === 0 ? (
          <p className="text-sm text-by-muted">No restaurants linked yet.</p>
        ) : (
          <ul className="space-y-2">
            {place.nearby_restaurants.map((restaurant) => (
              <li key={restaurant.id}>
                <Link
                  to={`/restaurants/${restaurant.id}`}
                  className="block rounded-xl bg-by-saffron-soft px-3 py-2 text-sm hover:bg-by-saffron-soft/80"
                >
                  <span className="font-medium text-by-ink">{restaurant.name}</span>
                  {restaurant.cuisine_tags ? ` · ${restaurant.cuisine_tags}` : ''}
                  {restaurant.is_seed_data ? ' · Demo' : ''}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card className="space-y-3">
        <h2 className="text-lg font-semibold text-by-ink">Nearby services</h2>
        <p className="text-xs text-by-muted">
          These are unverified guidance notes — not official POI listings.
        </p>
        <ul className="space-y-2">
          {place.nearby_amenities.map((amenity) => (
            <li key={`${amenity.kind}-${amenity.name}`} className="rounded-xl border border-by-border px-3 py-2">
              <p className="text-sm font-medium text-by-ink">{amenity.name}</p>
              <p className="mt-1 text-xs text-by-muted">{amenity.note}</p>
            </li>
          ))}
        </ul>
      </Card>

      <div className="flex gap-3 text-sm">
        <Link to={ROUTES.explore} className="font-medium text-by-green hover:underline">
          ← Explore
        </Link>
        <Link to={ROUTES.home} className="font-medium text-by-blue hover:underline">
          Home
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

function NearbyList({
  title,
  empty,
  children,
}: {
  title: string
  empty: string
  children: ReactNode
}) {
  const hasItems = Boolean(children && (!Array.isArray(children) || children.length > 0))
  return (
    <section>
      <h2 className="mb-3 text-lg font-semibold text-by-ink">{title}</h2>
      {hasItems ? (
        <div className="scrollbar-hide -mx-4 flex gap-3 overflow-x-auto px-4 pb-1">{children}</div>
      ) : (
        <Card>
          <EmptyState title={empty} />
        </Card>
      )}
    </section>
  )
}
