export type ActivitySummary = {
  id: string
  name: string
  slug: string
  category: string
  description: string | null
  duration_hours: number | null
  price_inr: number
  latitude: number | null
  longitude: number | null
  rating_avg: number
  rating_count: number
  hero_image_url: string | null
  city_name: string
  state_name: string
  state_code: string
  is_available: boolean
  is_seed_data: boolean
  distance_km: number | null
  provenance: string
}

export type ActivityDetail = ActivitySummary & {
  safety_information: string | null
  data_notice: string
}

export type PaginatedActivities = {
  items: ActivitySummary[]
  meta: {
    page: number
    page_size: number
    total: number
    total_pages: number
  }
}
