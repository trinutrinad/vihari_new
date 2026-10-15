import { apiClient } from '@/services/api'
import type { ApiResponse } from '@/types/api'
import type {
  Coupon,
  PaymentCreateInput,
  PaymentDetail,
  PaymentSummary,
  Wallet,
} from '@/types/payments'

export async function listPayments(params?: {
  status?: string
  booking_id?: string
}) {
  const { data } = await apiClient.get<ApiResponse<PaymentSummary[]>>('/payments', {
    params,
  })
  return data
}

export async function getPayment(paymentId: string) {
  const { data } = await apiClient.get<ApiResponse<PaymentDetail>>(
    `/payments/${paymentId}`,
  )
  return data
}

export async function createPayment(payload: PaymentCreateInput) {
  const { data } = await apiClient.post<ApiResponse<PaymentDetail>>('/payments', payload)
  return data
}

export async function refundPayment(paymentId: string) {
  const { data } = await apiClient.post<ApiResponse<PaymentDetail>>(
    `/payments/${paymentId}/refund`,
  )
  return data
}

export async function getWallet() {
  const { data } = await apiClient.get<ApiResponse<Wallet>>('/wallet')
  return data
}

export async function topUpWallet(amountInr: number) {
  const { data } = await apiClient.post<ApiResponse<Wallet>>('/wallet/topup', {
    amount_inr: amountInr,
  })
  return data
}

export async function getCoupon(code: string) {
  const { data } = await apiClient.get<ApiResponse<Coupon>>(`/coupons/${code}`)
  return data
}
