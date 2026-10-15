export type PaymentMethod =
  | 'mock'
  | 'upi'
  | 'card'
  | 'net_banking'
  | 'wallet'
  | 'cash'

export type PaymentStatus =
  | 'pending'
  | 'authorized'
  | 'captured'
  | 'failed'
  | 'refunded'
  | 'cancelled'

export type PaymentSummary = {
  id: string
  payment_number: string
  booking_id: string | null
  booking_number: string | null
  amount_inr: number
  currency: string
  method: PaymentMethod | string
  status: PaymentStatus | string
  provider: string
  provider_reference: string | null
  coupon_code: string | null
  paid_at: string | null
  is_mock: boolean
  created_at: string | null
}

export type PaymentDetail = PaymentSummary & {
  failure_reason: string | null
  data_notice: string
}

export type PaymentCreateInput = {
  booking_id: string
  method?: PaymentMethod
  coupon_code?: string
}

export type Wallet = {
  id: string
  balance_inr: number
  currency: string
  is_active: boolean
  data_notice: string
}

export type Coupon = {
  code: string
  description: string | null
  discount_percent: number | null
  discount_amount_inr: number | null
  is_active: boolean
  is_seed_data: boolean
}
