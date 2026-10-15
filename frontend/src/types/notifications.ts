export type NotificationItem = {
  id: string
  title: string
  body: string
  category: string | null
  channel: string
  is_read: boolean
  read_at: string | null
  payload: Record<string, unknown> | null
  created_at: string | null
  data_notice: string
}

export type UnreadCount = {
  unread_count: number
}
