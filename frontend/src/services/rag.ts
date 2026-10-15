import { apiClient } from '@/services/api'
import type { ApiResponse } from '@/types/api'
import type { RagDocument, RagQueryResult } from '@/types/rag'

export async function queryRag(payload: { question: string; top_k?: number }) {
  const { data } = await apiClient.post<ApiResponse<RagQueryResult>>('/rag/query', payload)
  return data
}

export async function listRagDocuments(params?: { limit?: number }) {
  const { data } = await apiClient.get<ApiResponse<RagDocument[]>>('/rag/documents', {
    params,
  })
  return data
}

export async function seedRagDemo() {
  const { data } = await apiClient.post<ApiResponse<RagDocument[]>>('/rag/seed-demo')
  return data
}
