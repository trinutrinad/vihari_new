import { useNavigate } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States'
import { ROUTES } from '@/constants/app'
import {
  createDemoNotification,
  listNotifications,
  markAllNotificationsRead,
  markNotificationRead,
} from '@/services/notifications'
import { useAuthStore } from '@/store/auth'

export function NotificationsPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const tokens = useAuthStore((state) => state.tokens)

  const notificationsQuery = useQuery({
    queryKey: ['notifications'],
    queryFn: async () => {
      const response = await listNotifications({ limit: 50 })
      return response.data ?? []
    },
    enabled: Boolean(tokens?.access_token),
  })

  const markOne = useMutation({
    mutationFn: async (id: string) => markNotificationRead(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['notifications'] })
      await queryClient.invalidateQueries({ queryKey: ['notifications-unread'] })
    },
  })

  const markAll = useMutation({
    mutationFn: async () => markAllNotificationsRead(),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['notifications'] })
      await queryClient.invalidateQueries({ queryKey: ['notifications-unread'] })
    },
  })

  const demo = useMutation({
    mutationFn: async () => createDemoNotification(),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['notifications'] })
      await queryClient.invalidateQueries({ queryKey: ['notifications-unread'] })
    },
  })

  if (!tokens?.access_token) {
    return (
      <Card className="space-y-4 text-left">
        <h2 className="font-display text-2xl font-semibold text-by-ink">Notifications</h2>
        <p className="text-sm text-by-muted">
          Sign in to see booking, payment, and safety alerts in your inbox.
        </p>
        <Button onClick={() => navigate(ROUTES.login)}>Sign in</Button>
      </Card>
    )
  }

  const items = notificationsQuery.data ?? []
  const unread = items.filter((item) => !item.is_read).length

  return (
    <div className="flex flex-col gap-5 text-left">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="font-display text-2xl font-semibold text-by-ink">Notifications</h2>
          <p className="mt-1 text-sm text-by-muted">
            In-app alerts for now. Push/SMS/email arrive later.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            size="sm"
            variant="ghost"
            disabled={demo.isPending}
            onClick={() => demo.mutate()}
          >
            {demo.isPending ? 'Sending…' : 'Send demo'}
          </Button>
          <Button
            size="sm"
            variant="secondary"
            disabled={markAll.isPending || unread === 0}
            onClick={() => markAll.mutate()}
          >
            Mark all read
          </Button>
        </div>
      </div>

      {unread > 0 ? <Badge tone="saffron">{unread} unread</Badge> : null}

      {notificationsQuery.isLoading ? (
        <LoadingState label="Loading notifications…" />
      ) : null}
      {notificationsQuery.isError ? (
        <ErrorState
          title="Could not load notifications"
          actionLabel="Retry"
          onAction={() => void notificationsQuery.refetch()}
        />
      ) : null}

      {!notificationsQuery.isLoading && items.length === 0 ? (
        <Card>
          <EmptyState
            title="Inbox empty"
            description="Book something, pay, or tap Send demo to create a sample alert."
            actionLabel="Browse hotels"
            onAction={() => navigate(ROUTES.hotels)}
          />
        </Card>
      ) : null}

      <ul className="space-y-3">
        {items.map((item) => {
          const href =
            typeof item.payload?.href === 'string' ? item.payload.href : null
          return (
            <li key={item.id}>
              <button
                type="button"
                className={`w-full rounded-[1.25rem] border px-4 py-3 text-left shadow-[var(--shadow-by-card)] transition hover:border-by-saffron/40 ${
                  item.is_read
                    ? 'border-by-border bg-white'
                    : 'border-by-saffron/30 bg-by-saffron-soft/30'
                }`}
                onClick={() => {
                  if (!item.is_read) markOne.mutate(item.id)
                  if (href) navigate(href)
                }}
              >
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <p className="font-semibold text-by-ink">{item.title}</p>
                    <p className="mt-1 text-sm text-by-muted">{item.body}</p>
                    <p className="mt-2 text-xs text-by-muted">
                      {item.category ?? 'general'}
                      {item.created_at
                        ? ` · ${new Date(item.created_at).toLocaleString()}`
                        : ''}
                    </p>
                  </div>
                  {!item.is_read ? <Badge tone="saffron">New</Badge> : null}
                </div>
              </button>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
