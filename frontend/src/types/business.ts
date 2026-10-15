export type BusinessAccess = {
  has_access: boolean
  roles: string[]
  hotels_count: number
  restaurants_count: number
  guides_count: number
}

export type BusinessSummary = {
  hotels_count: number
  restaurants_count: number
  guides_count: number
  bookings_total: number
  bookings_pending: number
  bookings_confirmed: number
  bookings_cancelled: number
  bookings_completed: number
  revenue_captured_inr: number
  data_notice: string
}

export type BusinessProperty = {
  id: string
  resource_type: string
  name: string
  slug: string | null
  city_name: string | null
  rating_avg: number | null
  rating_count: number
  href: string | null
  is_seed_data: boolean
}

export type BusinessBooking = {
  id: string
  booking_number: string
  resource_type: string
  resource_id: string
  resource_title: string
  status: string
  amount_inr: number
  currency: string
  scheduled_at: string | null
  location_text: string | null
  created_at: string | null
  is_mock: boolean
}
