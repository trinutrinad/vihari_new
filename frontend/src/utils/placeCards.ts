import type { HomePlace } from '@/types/place'
import type { PlaceSummary } from '@/types/places'
import type { PlaceCardModel } from '@/components/ui/PlaceCard'

const COVER: Record<string, string> = {
  temple: 'from-[#1b7a4e] to-[#0b3d91]',
  Temples: 'from-[#1b7a4e] to-[#0b3d91]',
  beach: 'from-[#0b3d91] to-[#1b7a4e]',
  Beaches: 'from-[#0b3d91] to-[#1b7a4e]',
  mountain: 'from-[#145c3b] to-[#5c6b63]',
  Mountains: 'from-[#145c3b] to-[#5c6b63]',
  waterfall: 'from-[#0b3d91] to-[#5c6b63]',
  Waterfalls: 'from-[#0b3d91] to-[#5c6b63]',
  historical: 'from-[#e07a2f] to-[#1b7a4e]',
  Historical: 'from-[#e07a2f] to-[#1b7a4e]',
  wildlife: 'from-[#145c3b] to-[#e07a2f]',
  Wildlife: 'from-[#145c3b] to-[#e07a2f]',
  nature: 'from-[#1b7a4e] to-[#145c3b]',
  Nature: 'from-[#1b7a4e] to-[#145c3b]',
  city: 'from-[#0b3d91] to-[#14201a]',
  City: 'from-[#0b3d91] to-[#14201a]',
  food: 'from-[#e07a2f] to-[#0b3d91]',
  Food: 'from-[#e07a2f] to-[#0b3d91]',
}

export function homePlaceToCard(place: HomePlace): PlaceCardModel {
  return {
    id: place.id,
    name: place.name,
    locationLabel: `${place.location}, ${place.state}`,
    categoryLabel: place.category,
    rating: place.rating,
    distanceKm: place.distanceKm,
    estimatedCostInr: place.estimatedCostInr,
    coverClassName: place.imageUrl.startsWith('from-') ? place.imageUrl : COVER[place.category],
    imageUrl: place.imageUrl.startsWith('from-') ? null : place.imageUrl,
    isDemo: place.isDemo,
  }
}

export function apiPlaceToCard(place: PlaceSummary): PlaceCardModel {
  const categoryKey = place.category?.slug ?? place.category?.name ?? 'city'
  return {
    id: place.id,
    name: place.name,
    locationLabel: `${place.city_name}, ${place.state_name}`,
    categoryLabel: place.category?.name ?? 'Place',
    rating: Number(place.rating_avg),
    distanceKm: place.distance_km,
    estimatedCostInr: place.estimated_cost_inr,
    coverClassName: COVER[categoryKey] ?? COVER.city,
    imageUrl: place.hero_image_url,
    isDemo: place.is_seed_data,
  }
}
