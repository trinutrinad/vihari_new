export type BookingResourceType =
  | 'hotel'
  | 'guide'
  | 'activity'
  | 'transport'
  | 'restaurant'

export type BookingStatus =
  | 'pending'
  | 'confirmed'
  | 'in_progress'
  | 'completed'
  | 'cancelled'
  | 'failed'

export type BookingSummary = {
  id: string
  booking_number: string
  resource_type: BookingResourceType | string
  resource_id: string
  resource_title: string
  resource_href: string | null
  status: BookingStatus | string
  scheduled_at: string | null
  amount_inr: number
  currency: string
  provider: string | null
  location_text: string | null
  is_mock: boolean
  created_at: string | null
}

export type BookingDetail = BookingSummary & {
  cancellation_reason: string | null
  notes: string | null
  metadata: Record<string, unknown> | null
  data_notice: string
}

export type BookingCreateInput = {
  resource_type: BookingResourceType
  resource_id: string
  scheduled_at?: string
  notes?: string
  nights?: number
  duration_days?: number
  participants?: number
  distance_km?: number
}
