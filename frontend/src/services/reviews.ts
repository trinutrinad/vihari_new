import { apiClient } from '@/services/api'
import type { ApiResponse } from '@/types/api'
import type { Review, ReviewCreateInput, ReviewTargetType } from '@/types/reviews'

export async function listReviews(targetType: ReviewTargetType, targetId: string) {
  const { data } = await apiClient.get<ApiResponse<Review[]>>('/reviews', {
    params: { target_type: targetType, target_id: targetId },
  })
  return data
}

export async function listMyReviews() {
  const { data } = await apiClient.get<ApiResponse<Review[]>>('/reviews/me')
  return data
}

export async function upsertReview(payload: ReviewCreateInput) {
  const { data } = await apiClient.post<ApiResponse<Review>>('/reviews', payload)
  return data
}

export async function deleteReview(reviewId: string) {
  const { data } = await apiClient.delete<ApiResponse<{ deleted: boolean }>>(
    `/reviews/${reviewId}`,
  )
  return data
}
