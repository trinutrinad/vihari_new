export type TripStatus =
  | 'draft'
  | 'upcoming'
  | 'active'
  | 'completed'
  | 'cancelled'

export type TripPlaceStop = {
  id: string
  place_id: string | null
  custom_title: string | null
  title: string
  time_slot: string | null
  notes: string | null
  estimated_cost_inr: number | null
  sort_order: number
  place_slug: string | null
  city_name: string | null
  latitude: number | null
  longitude: number | null
  is_seed_data: boolean
}

export type TripDay = {
  id: string
  day_number: number
  title: string | null
  notes: string | null
  places: TripPlaceStop[]
}

export type TripMapPoint = {
  id: string
  label: string
  day_number: number
  latitude: number
  longitude: number
  href: string | null
}

export type TripSummary = {
  id: string
  title: string
  summary: string | null
  start_date: string | null
  end_date: string | null
  origin_city: string | null
  destination_summary: string | null
  budget_inr: number | null
  estimated_cost_inr: number | null
  status: TripStatus | string
  is_ai_generated: boolean
  share_code: string | null
  day_count: number
  stop_count: number
  created_at: string
  updated_at: string
}

export type TripDetail = TripSummary & {
  days: TripDay[]
  map_points: TripMapPoint[]
}

export type TripShare = {
  share_code: string
  share_path: string
}

export type TripCreatePayload = {
  title: string
  summary?: string
  start_date?: string
  end_date?: string
  origin_city?: string
  destination_summary?: string
  budget_inr?: number
  status?: TripStatus
  days?: Array<{
    day_number: number
    title?: string
    notes?: string
    places?: Array<{
      place_id?: string
      custom_title?: string
      time_slot?: string
      notes?: string
      estimated_cost_inr?: number
      sort_order?: number
    }>
  }>
}
