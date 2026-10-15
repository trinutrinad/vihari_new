export type PlaceCategory = {
  id: string
  name: string
  slug: string
  icon: string | null
}

export type PlaceSummary = {
  id: string
  name: string
  slug: string
  short_description: string | null
  city_name: string
  state_name: string
  state_code: string
  category: PlaceCategory | null
  latitude: number | null
  longitude: number | null
  rating_avg: number
  rating_count: number
  estimated_cost_inr: number | null
  hero_image_url: string | null
  is_featured: boolean
  is_hidden_gem: boolean
  is_family_friendly: boolean
  is_couple_friendly: boolean
  is_pet_friendly: boolean
  provenance: string
  is_seed_data: boolean
  distance_km: number | null
}

export type NearbyAmenity = {
  name: string
  kind: string
  note: string
  provenance: string
}

export type PlaceDetail = PlaceSummary & {
  description: string | null
  address: string | null
  best_time_to_visit: string | null
  opening_hours: string | null
  entry_fee_notes: string | null
  facilities: string | null
  how_to_reach: string | null
  images: Array<{
    id: string
    url: string
    caption: string | null
    is_cover: boolean
    sort_order: number
  }>
  nearby_places: PlaceSummary[]
  nearby_hotels: Array<{
    id: string
    name: string
    slug: string
    rating_avg: number
    starting_price_inr: number | null
    is_seed_data: boolean
  }>
  nearby_restaurants: Array<{
    id: string
    name: string
    slug: string
    rating_avg: number
    cuisine_tags: string | null
    is_seed_data: boolean
  }>
  nearby_amenities: NearbyAmenity[]
  is_saved: boolean
  data_notice: string
}

export type PageMeta = {
  page: number
  page_size: number
  total: number
  total_pages: number
}

export type PaginatedPlaces = {
  items: PlaceSummary[]
  meta: PageMeta
}
