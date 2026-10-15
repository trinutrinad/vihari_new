export type TransportOptionSummary = {
  id: string
  code: string
  name: string
  vehicle_type: string
  description: string | null
  base_fare_inr: number
  per_km_inr: number
  is_active: boolean
  is_seed_data: boolean
  sample_fare_10km_inr: number | null
  provenance: string
}

export type TransportOptionDetail = TransportOptionSummary & {
  data_notice: string
}

export type FareEstimate = {
  option_id: string
  code: string
  name: string
  vehicle_type: string
  distance_km: number
  base_fare_inr: number
  per_km_inr: number
  estimated_fare_inr: number | null
  currency: string
  is_estimate: boolean
  note: string
}

export type PaginatedTransport = {
  items: TransportOptionSummary[]
  meta: {
    page: number
    page_size: number
    total: number
    total_pages: number
  }
}
