import { apiClient } from '@/services/api'
import type { ApiResponse } from '@/types/api'
import type {
  TripCreatePayload,
  TripDetail,
  TripShare,
  TripSummary,
  TripStatus,
} from '@/types/trips'

export async function listTrips(status?: string) {
  const { data } = await apiClient.get<ApiResponse<TripSummary[]>>('/trips', {
    params: status ? { status } : undefined,
  })
  return data
}

export async function getTrip(tripId: string) {
  const { data } = await apiClient.get<ApiResponse<TripDetail>>(`/trips/${tripId}`)
  return data
}

export async function getSharedTrip(shareCode: string) {
  const { data } = await apiClient.get<ApiResponse<TripDetail>>(
    `/trips/shared/${shareCode}`,
  )
  return data
}

export async function createTrip(payload: TripCreatePayload) {
  const { data } = await apiClient.post<ApiResponse<TripDetail>>('/trips', payload)
  return data
}

export async function updateTrip(
  tripId: string,
  payload: Partial<{
    title: string
    summary: string
    start_date: string
    end_date: string
    origin_city: string
    destination_summary: string
    budget_inr: number
    status: TripStatus
  }>,
) {
  const { data } = await apiClient.patch<ApiResponse<TripDetail>>(
    `/trips/${tripId}`,
    payload,
  )
  return data
}

export async function deleteTrip(tripId: string) {
  const { data } = await apiClient.delete<ApiResponse<{ deleted: boolean }>>(
    `/trips/${tripId}`,
  )
  return data
}

export async function addTripDay(
  tripId: string,
  payload: { day_number: number; title?: string; notes?: string },
) {
  const { data } = await apiClient.post<ApiResponse<TripDetail>>(
    `/trips/${tripId}/days`,
    payload,
  )
  return data
}

export async function deleteTripDay(tripId: string, dayId: string) {
  const { data } = await apiClient.delete<ApiResponse<TripDetail>>(
    `/trips/${tripId}/days/${dayId}`,
  )
  return data
}

export async function addTripStop(
  tripId: string,
  dayId: string,
  payload: {
    place_id?: string
    custom_title?: string
    time_slot?: string
    notes?: string
    estimated_cost_inr?: number
  },
) {
  const { data } = await apiClient.post<ApiResponse<TripDetail>>(
    `/trips/${tripId}/days/${dayId}/places`,
    payload,
  )
  return data
}

export async function removeTripStop(tripId: string, dayId: string, stopId: string) {
  const { data } = await apiClient.delete<ApiResponse<TripDetail>>(
    `/trips/${tripId}/days/${dayId}/places/${stopId}`,
  )
  return data
}

export async function shareTrip(tripId: string) {
  const { data } = await apiClient.post<ApiResponse<TripShare>>(`/trips/${tripId}/share`)
  return data
}
