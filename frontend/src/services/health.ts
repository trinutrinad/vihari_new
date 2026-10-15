import { apiClient } from '@/services/api'
import type { ApiResponse, HealthData } from '@/types/api'

export async function getHealth(): Promise<ApiResponse<HealthData>> {
  const { data } = await apiClient.get<ApiResponse<HealthData>>('/health')
  return data
}

export async function getReadiness(): Promise<ApiResponse<HealthData>> {
  const { data } = await apiClient.get<ApiResponse<HealthData>>('/health/ready')
  return data
}
