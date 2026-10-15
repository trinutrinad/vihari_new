import { apiClient } from '@/services/api'
import type { ApiResponse } from '@/types/api'
import type {
  AutocompleteSuggestion,
  SearchResponseData,
  TrendingSearchesData,
} from '@/types/search'

export type GlobalSearchParams = {
  q?: string
  types?: string
  category?: string
  state?: string
  min_rating?: number
  max_cost?: number
  lat?: number
  lng?: number
  radius_km?: number
  page?: number
  page_size?: number
}

export async function globalSearch(params: GlobalSearchParams = {}) {
  const { data } = await apiClient.get<ApiResponse<SearchResponseData>>('/search', {
    params,
  })
  return data
}

export async function searchAutocomplete(q: string, limit = 8) {
  const { data } = await apiClient.get<ApiResponse<AutocompleteSuggestion[]>>(
    '/search/autocomplete',
    { params: { q, limit } },
  )
  return data
}

export async function searchTrending() {
  const { data } = await apiClient.get<ApiResponse<TrendingSearchesData>>('/search/trending')
  return data
}
