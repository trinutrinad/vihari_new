export type AdminAccess = {
  has_access: boolean
  roles: string[]
}

export type AdminSummary = {
  users_total: number
  users_active: number
  places_total: number
  hotels_total: number
  restaurants_total: number
  guides_total: number
  activities_total: number
  bookings_total: number
  bookings_open: number
  payments_captured_total: number
  revenue_captured_inr: number
  support_tickets_open: number
  seed_entities_total: number
  data_notice: string
}

export type AdminUser = {
  id: string
  full_name: string
  email: string | null
  phone: string | null
  primary_role: string
  is_active: boolean
  is_seed_data: boolean
  created_at: string | null
}

export type AdminBooking = {
  id: string
  booking_number: string
  resource_type: string
  resource_id: string
  status: string
  amount_inr: number
  currency: string
  user_id: string
  created_at: string | null
}

export type AdminPayment = {
  id: string
  payment_number: string
  amount_inr: number
  status: string
  method: string
  user_id: string
  booking_id: string | null
  is_mock: boolean
  created_at: string | null
}

export type AdminTicket = {
  id: string
  ticket_number: string
  subject: string
  status: string
  priority: string
  user_id: string
  created_at: string | null
}
