import { apiClient } from '@/services/api'
import type { ApiResponse } from '@/types/api'
import type { NotificationItem, UnreadCount } from '@/types/notifications'

export async function listNotifications(params?: {
  unread_only?: boolean
  limit?: number
}) {
  const { data } = await apiClient.get<ApiResponse<NotificationItem[]>>(
    '/notifications',
    { params },
  )
  return data
}

export async function getUnreadCount() {
  const { data } = await apiClient.get<ApiResponse<UnreadCount>>(
    '/notifications/unread-count',
  )
  return data
}

export async function markNotificationRead(notificationId: string) {
  const { data } = await apiClient.post<ApiResponse<NotificationItem>>(
    `/notifications/${notificationId}/read`,
  )
  return data
}

export async function markAllNotificationsRead() {
  const { data } = await apiClient.post<ApiResponse<UnreadCount>>(
    '/notifications/read-all',
  )
  return data
}

export async function createDemoNotification(payload?: {
  title?: string
  body?: string
  category?: string
}) {
  const { data } = await apiClient.post<ApiResponse<NotificationItem>>(
    '/notifications/demo',
    payload ?? {},
  )
  return data
}
