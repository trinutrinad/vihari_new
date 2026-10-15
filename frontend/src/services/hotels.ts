import { apiClient } from '@/services/api'
import type { ApiResponse } from '@/types/api'
import type { HotelDetail, HotelSummary, PaginatedHotels } from '@/types/hotels'

export type ListHotelsParams = {
  page?: number
  page_size?: number
  city?: string
  state?: string
  q?: string
  min_price?: number
  max_price?: number
  wifi?: boolean
  breakfast?: boolean
  parking?: boolean
  pool?: boolean
  family_friendly?: boolean
  lat?: number
  lng?: number
}

export async function listHotels(params: ListHotelsParams = {}) {
  const { data } = await apiClient.get<ApiResponse<PaginatedHotels>>('/hotels', {
    params,
  })
  return data
}

export async function getHotel(hotelId: string) {
  const { data } = await apiClient.get<ApiResponse<HotelDetail>>(`/hotels/${hotelId}`)
  return data
}

export async function getHotelBySlug(slug: string) {
  const { data } = await apiClient.get<ApiResponse<HotelDetail>>(`/hotels/by-slug/${slug}`)
  return data
}

export async function listNearbyHotels(lat: number, lng: number, radiusKm = 50) {
  const { data } = await apiClient.get<ApiResponse<HotelSummary[]>>('/hotels/nearby', {
    params: { lat, lng, radius_km: radiusKm },
  })
  return data
}
