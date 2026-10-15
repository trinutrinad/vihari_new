import { apiClient } from '@/services/api'
import type { ApiResponse } from '@/types/api'
import type {
  BookingCreateInput,
  BookingDetail,
  BookingSummary,
} from '@/types/bookings'

export async function listBookings(params?: {
  status?: string
  resource_type?: string
}) {
  const { data } = await apiClient.get<ApiResponse<BookingSummary[]>>('/bookings', {
    params,
  })
  return data
}

export async function getBooking(bookingId: string) {
  const { data } = await apiClient.get<ApiResponse<BookingDetail>>(
    `/bookings/${bookingId}`,
  )
  return data
}

export async function createBooking(payload: BookingCreateInput) {
  const { data } = await apiClient.post<ApiResponse<BookingDetail>>('/bookings', payload)
  return data
}

export async function cancelBooking(bookingId: string, reason?: string) {
  const { data } = await apiClient.post<ApiResponse<BookingDetail>>(
    `/bookings/${bookingId}/cancel`,
    { reason },
  )
  return data
}
