import { apiClient } from '@/services/api'
import type { ApiResponse } from '@/types/api'
import type {
  PaginatedRestaurants,
  RestaurantDetail,
  RestaurantSummary,
} from '@/types/restaurants'

export type ListRestaurantsParams = {
  page?: number
  page_size?: number
  city?: string
  state?: string
  q?: string
  cuisine?: string
  vegetarian?: boolean
  street_food?: boolean
  max_price_level?: number
  lat?: number
  lng?: number
}

export async function listRestaurants(params: ListRestaurantsParams = {}) {
  const { data } = await apiClient.get<ApiResponse<PaginatedRestaurants>>(
    '/restaurants',
    { params },
  )
  return data
}

export async function getRestaurant(restaurantId: string) {
  const { data } = await apiClient.get<ApiResponse<RestaurantDetail>>(
    `/restaurants/${restaurantId}`,
  )
  return data
}

export async function getRestaurantBySlug(slug: string) {
  const { data } = await apiClient.get<ApiResponse<RestaurantDetail>>(
    `/restaurants/by-slug/${slug}`,
  )
  return data
}

export async function listNearbyRestaurants(lat: number, lng: number, radiusKm = 50) {
  const { data } = await apiClient.get<ApiResponse<RestaurantSummary[]>>(
    '/restaurants/nearby',
    { params: { lat, lng, radius_km: radiusKm } },
  )
  return data
}
