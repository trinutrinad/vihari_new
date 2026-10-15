export type HotelSummary = {
  id: string
  name: string
  slug: string
  description: string | null
  city_name: string
  state_name: string
  state_code: string
  latitude: number | null
  longitude: number | null
  rating_avg: number
  rating_count: number
  starting_price_inr: number | null
  has_ac: boolean
  has_wifi: boolean
  has_parking: boolean
  has_breakfast: boolean
  has_pool: boolean
  is_family_friendly: boolean
  is_couple_friendly: boolean
  hero_image_url: string | null
  is_seed_data: boolean
  distance_km: number | null
  provenance: string
}

export type HotelRoom = {
  id: string
  name: string
  description: string | null
  max_guests: number
  price_per_night_inr: number
  total_rooms: number
  is_available: boolean
}

export type HotelDetail = HotelSummary & {
  address: string | null
  cancellation_policy: string | null
  rooms: HotelRoom[]
  data_notice: string
}

export type PaginatedHotels = {
  items: HotelSummary[]
  meta: {
    page: number
    page_size: number
    total: number
    total_pages: number
  }
}
