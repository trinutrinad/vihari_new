import { apiClient } from '@/services/api'
import type { ApiResponse } from '@/types/api'
import type {
  PaginatedPlaces,
  PlaceCategory,
  PlaceDetail,
  PlaceSummary,
} from '@/types/places'

export type ListPlacesParams = {
  page?: number
  page_size?: number
  category?: string
  state?: string
  city?: string
  featured?: boolean
  hidden_gem?: boolean
  family_friendly?: boolean
  q?: string
  lat?: number
  lng?: number
}

export async function listPlaces(params: ListPlacesParams = {}) {
  const { data } = await apiClient.get<ApiResponse<PaginatedPlaces>>('/places', {
    params,
  })
  return data
}

export async function listPlaceCategories() {
  const { data } = await apiClient.get<ApiResponse<PlaceCategory[]>>('/places/categories')
  return data
}

export async function getPlace(placeId: string) {
  const { data } = await apiClient.get<ApiResponse<PlaceDetail>>(`/places/${placeId}`)
  return data
}

export async function getPlaceBySlug(slug: string) {
  const { data } = await apiClient.get<ApiResponse<PlaceDetail>>(
    `/places/by-slug/${slug}`,
  )
  return data
}

export async function listNearbyPlaces(lat: number, lng: number, radiusKm = 50) {
  const { data } = await apiClient.get<ApiResponse<PlaceSummary[]>>('/places/nearby', {
    params: { lat, lng, radius_km: radiusKm },
  })
  return data
}

export async function savePlace(placeId: string) {
  const { data } = await apiClient.post<ApiResponse<{ place_id: string; saved: boolean }>>(
    `/places/${placeId}/save`,
  )
  return data
}

export async function unsavePlace(placeId: string) {
  const { data } = await apiClient.delete<
    ApiResponse<{ place_id: string; saved: boolean }>
  >(`/places/${placeId}/save`)
  return data
}

export async function listSavedPlaces() {
  const { data } = await apiClient.get<ApiResponse<PlaceSummary[]>>('/places/saved')
  return data
}
