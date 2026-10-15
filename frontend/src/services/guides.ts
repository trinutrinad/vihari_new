import { apiClient } from '@/services/api'
import type { ApiResponse } from '@/types/api'
import type { GuideDetail, GuideSummary, PaginatedGuides } from '@/types/guides'

export type ListGuidesParams = {
  page?: number
  page_size?: number
  city?: string
  state?: string
  q?: string
  language?: string
  specialization?: string
  max_price?: number
  lat?: number
  lng?: number
}

export async function listGuides(params: ListGuidesParams = {}) {
  const { data } = await apiClient.get<ApiResponse<PaginatedGuides>>('/guides', {
    params,
  })
  return data
}

export async function getGuide(guideId: string) {
  const { data } = await apiClient.get<ApiResponse<GuideDetail>>(`/guides/${guideId}`)
  return data
}

export async function listNearbyGuides(lat: number, lng: number, radiusKm = 80) {
  const { data } = await apiClient.get<ApiResponse<GuideSummary[]>>('/guides/nearby', {
    params: { lat, lng, radius_km: radiusKm },
  })
  return data
}
