export type ReviewTargetType =
  | 'place'
  | 'hotel'
  | 'restaurant'
  | 'guide'
  | 'activity'

export type Review = {
  id: string
  target_type: ReviewTargetType | string
  target_id: string
  user_id: string
  rating: number
  title: string | null
  body: string | null
  author_name: string
  is_visible: boolean
  is_moderated: boolean
  created_at: string | null
  updated_at: string | null
  data_notice: string
}

export type ReviewCreateInput = {
  target_type: ReviewTargetType
  target_id: string
  rating: number
  title?: string
  body?: string
}
