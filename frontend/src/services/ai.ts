import { apiClient } from '@/services/api'
import type { ApiResponse } from '@/types/api'
import type { AgentInfo, ChatResult, PlanTripPayload, PlanTripResult } from '@/types/ai'

export async function planTrip(payload: PlanTripPayload) {
  const { data } = await apiClient.post<ApiResponse<PlanTripResult>>(
    '/ai/plan-trip',
    payload,
  )
  return data
}

export async function aiChat(message: string, conversationId?: string) {
  const { data } = await apiClient.post<ApiResponse<ChatResult>>('/ai/chat', {
    message,
    conversation_id: conversationId,
  })
  return data
}

export async function listAiAgents() {
  const { data } = await apiClient.get<ApiResponse<AgentInfo[]>>('/ai/agents')
  return data
}
