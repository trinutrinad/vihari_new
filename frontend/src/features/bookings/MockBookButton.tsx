import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Button } from '@/components/ui/Button'
import { ROUTES } from '@/constants/app'
import { createBooking } from '@/services/bookings'
import { useAuthStore } from '@/store/auth'
import type { BookingCreateInput, BookingResourceType } from '@/types/bookings'

export type MockBookButtonProps = {
  resourceType: BookingResourceType
  resourceId: string
  label?: string
  extras?: Omit<BookingCreateInput, 'resource_type' | 'resource_id'>
}

export function MockBookButton({
  resourceType,
  resourceId,
  label = 'Book (mock)',
  extras,
}: MockBookButtonProps) {
  const navigate = useNavigate()
  const tokens = useAuthStore((state) => state.tokens)
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: async () =>
      createBooking({
        resource_type: resourceType,
        resource_id: resourceId,
        ...extras,
      }),
    onSuccess: (response) => {
      setError(null)
      if (response.data?.id) navigate(`/bookings/${response.data.id}`)
      else navigate(ROUTES.bookings)
    },
    onError: (err: Error) => {
      setError(err.message || 'Could not create mock booking')
    },
  })

  if (!tokens?.access_token) {
    return (
      <Button
        size="sm"
        variant="secondary"
        onClick={() => navigate(`${ROUTES.login}?next=${encodeURIComponent(window.location.pathname)}`)}
      >
        Sign in to book
      </Button>
    )
  }

  return (
    <div className="space-y-2">
      <Button
        size="sm"
        variant="secondary"
        disabled={mutation.isPending}
        onClick={() => mutation.mutate()}
      >
        {mutation.isPending ? 'Confirming…' : label}
      </Button>
      {error ? <p className="text-xs text-red-600">{error}</p> : null}
    </div>
  )
}
