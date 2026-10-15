import { apiClient } from '@/services/api'
import type { ApiResponse } from '@/types/api'
import type {
  FareEstimate,
  PaginatedTransport,
  TransportOptionDetail,
} from '@/types/transport'

export type ListTransportParams = {
  page?: number
  page_size?: number
  q?: string
  vehicle_type?: string
  max_base_fare?: number
}

export async function listTransportOptions(params: ListTransportParams = {}) {
  const { data } = await apiClient.get<ApiResponse<PaginatedTransport>>('/transport', {
    params,
  })
  return data
}

export async function getTransportOption(optionId: string) {
  const { data } = await apiClient.get<ApiResponse<TransportOptionDetail>>(
    `/transport/${optionId}`,
  )
  return data
}

export async function getTransportByCode(code: string) {
  const { data } = await apiClient.get<ApiResponse<TransportOptionDetail>>(
    `/transport/by-code/${code}`,
  )
  return data
}

export async function estimateTransportFare(params: {
  distance_km: number
  code?: string
  option_id?: string
}) {
  const { data } = await apiClient.get<ApiResponse<FareEstimate>>('/transport/estimate', {
    params,
  })
  return data
}
