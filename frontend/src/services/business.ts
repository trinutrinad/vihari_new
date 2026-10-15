import { apiClient } from '@/services/api'
import type { ApiResponse } from '@/types/api'
import type {
  BusinessAccess,
  BusinessBooking,
  BusinessProperty,
  BusinessSummary,
} from '@/types/business'

export async function fetchBusinessAccess() {
  const { data } = await apiClient.get<ApiResponse<BusinessAccess>>('/business/access')
  return data
}

export async function fetchBusinessSummary() {
  const { data } = await apiClient.get<ApiResponse<BusinessSummary>>('/business/summary')
  return data
}

export async function fetchBusinessProperties() {
  const { data } = await apiClient.get<ApiResponse<BusinessProperty[]>>('/business/properties')
  return data
}

export async function fetchBusinessBookings(params?: { limit?: number }) {
  const { data } = await apiClient.get<ApiResponse<BusinessBooking[]>>('/business/bookings', {
    params,
  })
  return data
}
