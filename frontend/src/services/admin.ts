import { apiClient } from '@/services/api'
import type { ApiResponse } from '@/types/api'
import type {
  AdminAccess,
  AdminBooking,
  AdminPayment,
  AdminSummary,
  AdminTicket,
  AdminUser,
} from '@/types/admin'

export async function fetchAdminAccess() {
  const { data } = await apiClient.get<ApiResponse<AdminAccess>>('/admin/access')
  return data
}

export async function fetchAdminSummary() {
  const { data } = await apiClient.get<ApiResponse<AdminSummary>>('/admin/summary')
  return data
}

export async function fetchAdminUsers(params?: { limit?: number }) {
  const { data } = await apiClient.get<ApiResponse<AdminUser[]>>('/admin/users', { params })
  return data
}

export async function fetchAdminBookings(params?: { limit?: number }) {
  const { data } = await apiClient.get<ApiResponse<AdminBooking[]>>('/admin/bookings', {
    params,
  })
  return data
}

export async function fetchAdminPayments(params?: { limit?: number }) {
  const { data } = await apiClient.get<ApiResponse<AdminPayment[]>>('/admin/payments', {
    params,
  })
  return data
}

export async function fetchAdminTickets(params?: { limit?: number; open_only?: boolean }) {
  const { data } = await apiClient.get<ApiResponse<AdminTicket[]>>('/admin/tickets', {
    params,
  })
  return data
}
