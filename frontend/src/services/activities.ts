import { apiClient } from '@/services/api'
import type { ApiResponse } from '@/types/api'
import type {
  ActivityDetail,
  ActivitySummary,
  PaginatedActivities,
} from '@/types/activities'

export type ListActivitiesParams = {
  page?: number
  page_size?: number
  city?: string
  state?: string
  q?: string
  category?: string
  max_price?: number
  lat?: number
  lng?: number
}

export async function listActivities(params: ListActivitiesParams = {}) {
  const { data } = await apiClient.get<ApiResponse<PaginatedActivities>>('/activities', {
    params,
  })
  return data
}

export async function getActivity(activityId: string) {
  const { data } = await apiClient.get<ApiResponse<ActivityDetail>>(
    `/activities/${activityId}`,
  )
  return data
}

export async function getActivityBySlug(slug: string) {
  const { data } = await apiClient.get<ApiResponse<ActivityDetail>>(
    `/activities/by-slug/${slug}`,
  )
  return data
}

export async function listNearbyActivities(lat: number, lng: number, radiusKm = 80) {
  const { data } = await apiClient.get<ApiResponse<ActivitySummary[]>>(
    '/activities/nearby',
    { params: { lat, lng, radius_km: radiusKm } },
  )
  return data
}
