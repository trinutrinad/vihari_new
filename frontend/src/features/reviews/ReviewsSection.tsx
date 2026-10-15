import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Rating } from '@/components/ui/Rating'
import { LoadingState } from '@/components/feedback/States'
import { ROUTES } from '@/constants/app'
import { deleteReview, listReviews, upsertReview } from '@/services/reviews'
import { useAuthStore } from '@/store/auth'
import type { ReviewTargetType } from '@/types/reviews'

export type ReviewsSectionProps = {
  targetType: ReviewTargetType
  targetId: string
}

export function ReviewsSection({ targetType, targetId }: ReviewsSectionProps) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const tokens = useAuthStore((state) => state.tokens)
  const user = useAuthStore((state) => state.user)
  const [rating, setRating] = useState(5)
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [error, setError] = useState<string | null>(null)

  const reviewsQuery = useQuery({
    queryKey: ['reviews', targetType, targetId],
    queryFn: async () => {
      const response = await listReviews(targetType, targetId)
      return response.data ?? []
    },
    enabled: Boolean(targetId),
  })

  const saveMutation = useMutation({
    mutationFn: async () =>
      upsertReview({
        target_type: targetType,
        target_id: targetId,
        rating,
        title: title.trim() || undefined,
        body: body.trim() || undefined,
      }),
    onSuccess: async () => {
      setError(null)
      setTitle('')
      setBody('')
      await queryClient.invalidateQueries({ queryKey: ['reviews', targetType, targetId] })
      await queryClient.invalidateQueries({ queryKey: [targetType] })
    },
    onError: (err: Error) => setError(err.message || 'Could not save review'),
  })

  const deleteMutation = useMutation({
    mutationFn: async (reviewId: string) => deleteReview(reviewId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['reviews', targetType, targetId] })
    },
  })

  const reviews = reviewsQuery.data ?? []

  return (
    <Card className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-by-ink">Reviews</h2>
        <p className="mt-1 text-xs text-by-muted">
          Community feedback. Demo reviews are fictional when seeded.
        </p>
      </div>

      {reviewsQuery.isLoading ? <LoadingState label="Loading reviews…" /> : null}

      {reviews.length === 0 && !reviewsQuery.isLoading ? (
        <p className="text-sm text-by-muted">No reviews yet. Be the first to share.</p>
      ) : null}

      <ul className="space-y-3">
        {reviews.map((review) => (
          <li
            key={review.id}
            className="rounded-xl border border-by-border/70 bg-by-green-soft/40 px-3 py-3"
          >
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <p className="text-sm font-medium text-by-ink">
                  {review.title || review.author_name}
                </p>
                <p className="mt-0.5 text-xs text-by-muted">
                  {review.author_name}
                  {review.created_at
                    ? ` · ${new Date(review.created_at).toLocaleDateString()}`
                    : ''}
                </p>
              </div>
              <Rating value={review.rating} />
            </div>
            {review.body ? (
              <p className="mt-2 text-sm text-by-muted">{review.body}</p>
            ) : null}
            {user?.id === review.user_id && tokens?.access_token ? (
              <Button
                size="sm"
                variant="ghost"
                className="mt-2"
                disabled={deleteMutation.isPending}
                onClick={() => deleteMutation.mutate(review.id)}
              >
                Remove
              </Button>
            ) : null}
          </li>
        ))}
      </ul>

      {!tokens?.access_token ? (
        <Button size="sm" variant="secondary" onClick={() => navigate(ROUTES.login)}>
          Sign in to review
        </Button>
      ) : (
        <div className="space-y-3 border-t border-by-border pt-4">
          <p className="text-sm font-medium text-by-ink">Write a review</p>
          <div className="flex flex-wrap gap-2">
            {[1, 2, 3, 4, 5].map((value) => (
              <Button
                key={value}
                size="sm"
                variant={rating === value ? 'saffron' : 'ghost'}
                onClick={() => setRating(value)}
              >
                {value}★
              </Button>
            ))}
          </div>
          {targetType === 'place' ? (
            <input
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="Title (optional)"
              className="w-full rounded-xl border border-by-border bg-white px-3 py-2 text-sm text-by-ink outline-none focus:border-by-green"
            />
          ) : null}
          <textarea
            value={body}
            onChange={(event) => setBody(event.target.value)}
            placeholder="Share your experience…"
            rows={3}
            className="w-full rounded-xl border border-by-border bg-white px-3 py-2 text-sm text-by-ink outline-none focus:border-by-green"
          />
          <div className="flex flex-wrap items-center gap-2">
            <Button
              size="sm"
              variant="secondary"
              disabled={saveMutation.isPending}
              onClick={() => saveMutation.mutate()}
            >
              {saveMutation.isPending ? 'Saving…' : 'Submit review'}
            </Button>
            <Badge tone="neutral">Upserts your previous review</Badge>
          </div>
          {error ? <p className="text-xs text-red-600">{error}</p> : null}
        </div>
      )}
    </Card>
  )
}
