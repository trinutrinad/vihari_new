import { apiClient } from '@/services/api'
import type { ApiResponse } from '@/types/api'
import type { CityMapCenter, MapPinsData } from '@/types/maps'
import type { MapBounds } from '@/features/maps/mapProvider'

export type MapPinsParams = MapBounds & {
  category?: string
  limit?: number
}

export async function fetchMapPins(params: MapPinsParams) {
  const { data } = await apiClient.get<ApiResponse<MapPinsData>>('/maps/pins', {
    params,
  })
  return data
}

export async function fetchMapCities(limit = 20) {
  const { data } = await apiClient.get<ApiResponse<CityMapCenter[]>>('/maps/cities', {
    params: { limit },
  })
  return data
}
