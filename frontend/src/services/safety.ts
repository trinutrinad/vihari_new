import { apiClient } from '@/services/api'
import type { ApiResponse } from '@/types/api'
import type {
  EmergencyContact,
  EmergencyContactInput,
  EmergencyNumber,
  SafetyTips,
  SosResult,
} from '@/types/safety'

export async function getSafetyTips(city?: string) {
  const { data } = await apiClient.get<ApiResponse<SafetyTips>>('/safety/tips', {
    params: city ? { city } : undefined,
  })
  return data
}

export async function listEmergencyNumbers() {
  const { data } = await apiClient.get<ApiResponse<EmergencyNumber[]>>(
    '/safety/emergency-numbers',
  )
  return data
}

export async function listEmergencyContacts() {
  const { data } = await apiClient.get<ApiResponse<EmergencyContact[]>>(
    '/safety/contacts',
  )
  return data
}

export async function createEmergencyContact(payload: EmergencyContactInput) {
  const { data } = await apiClient.post<ApiResponse<EmergencyContact>>(
    '/safety/contacts',
    payload,
  )
  return data
}

export async function deleteEmergencyContact(contactId: string) {
  const { data } = await apiClient.delete<ApiResponse<{ deleted: boolean }>>(
    `/safety/contacts/${contactId}`,
  )
  return data
}

export async function triggerMockSos(payload: {
  message?: string
  city?: string
  latitude?: number
  longitude?: number
}) {
  const { data } = await apiClient.post<ApiResponse<SosResult>>('/safety/sos', payload)
  return data
}
