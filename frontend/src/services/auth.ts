import { apiClient } from '@/services/api'
import type { ApiResponse } from '@/types/api'
import type { AuthSession, AuthUser } from '@/types/auth'

export async function registerAccount(input: {
  full_name: string
  email?: string
  phone?: string
  password: string
}) {
  const { data } = await apiClient.post<ApiResponse<AuthSession>>('/auth/register', input)
  return data
}

export async function loginAccount(input: {
  email?: string
  phone?: string
  password: string
}) {
  const { data } = await apiClient.post<ApiResponse<AuthSession>>('/auth/login', input)
  return data
}

export async function logoutAccount(refreshToken?: string | null) {
  const { data } = await apiClient.post<ApiResponse<{ message: string }>>('/auth/logout', {
    refresh_token: refreshToken ?? null,
  })
  return data
}

export async function fetchMe() {
  const { data } = await apiClient.get<ApiResponse<AuthUser>>('/auth/me')
  return data
}

export async function updateProfile(input: {
  full_name?: string
  bio?: string
  preferred_language?: string
  home_city?: string
  travel_preferences?: string[]
}) {
  const { data } = await apiClient.patch<ApiResponse<AuthUser>>('/auth/me/profile', input)
  return data
}

export async function forgotPassword(email: string) {
  const { data } = await apiClient.post<
    ApiResponse<{ message: string; reset_token?: string | null }>
  >('/auth/forgot-password', { email })
  return data
}

export async function resetPassword(token: string, new_password: string) {
  const { data } = await apiClient.post<ApiResponse<{ message: string }>>(
    '/auth/reset-password',
    { token, new_password },
  )
  return data
}

export async function requestPhoneOtp(phone: string) {
  const { data } = await apiClient.post<
    ApiResponse<{
      challenge_id: string
      expires_at: string
      provider: string
      is_mock: boolean
      message: string
      debug_code?: string
    }>
  >('/auth/phone/request-otp', { phone, purpose: 'login' })
  return data
}

export async function verifyPhoneOtp(input: {
  challenge_id: string
  code: string
  full_name?: string
}) {
  const { data } = await apiClient.post<ApiResponse<AuthSession>>(
    '/auth/phone/verify-otp',
    input,
  )
  return data
}
