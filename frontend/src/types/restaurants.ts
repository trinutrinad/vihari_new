export type RestaurantSummary = {
  id: string
  name: string
  slug: string
  description: string | null
  cuisine_tags: string | null
  city_name: string
  state_name: string
  state_code: string
  latitude: number | null
  longitude: number | null
  rating_avg: number
  rating_count: number
  price_level: number
  is_vegetarian: boolean
  is_street_food: boolean
  hero_image_url: string | null
  is_seed_data: boolean
  distance_km: number | null
  provenance: string
}

export type MenuItem = {
  id: string
  name: string
  description: string | null
  price_inr: number
  is_veg: boolean
  is_available: boolean
}

export type RestaurantDetail = RestaurantSummary & {
  address: string | null
  opening_hours: string | null
  menu_items: MenuItem[]
  data_notice: string
}

export type PaginatedRestaurants = {
  items: RestaurantSummary[]
  meta: {
    page: number
    page_size: number
    total: number
    total_pages: number
  }
}
