export type GuideSummary = {
  id: string
  display_name: string
  bio: string | null
  languages: string
  specialization: string | null
  experience_years: number
  price_per_day_inr: number
  rating_avg: number
  rating_count: number
  profile_image_url: string | null
  city_name: string
  state_name: string
  state_code: string
  latitude: number | null
  longitude: number | null
  is_active: boolean
  is_seed_data: boolean
  distance_km: number | null
  provenance: string
}

export type GuideAvailability = {
  id: string
  available_date: string
  is_available: boolean
}

export type GuideDetail = GuideSummary & {
  availability: GuideAvailability[]
  data_notice: string
}

export type PaginatedGuides = {
  items: GuideSummary[]
  meta: {
    page: number
    page_size: number
    total: number
    total_pages: number
  }
}
