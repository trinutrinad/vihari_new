export type ApiResponse<T> = {
  success: boolean
  message: string
  data: T | null
}

export type HealthData = {
  status: string
  service: string
  environment: string
  timestamp: string
  version: string
  checks?: Record<string, string> | null
}
