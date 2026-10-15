import { apiClient } from '@/services/api'
import type { ApiResponse } from '@/types/api'
import type { EvalCase, EvalRun } from '@/types/aiEval'

export async function listEvalCases() {
  const { data } = await apiClient.get<ApiResponse<EvalCase[]>>('/ai/eval/cases')
  return data
}

export async function runEvalSuite(payload?: { case_ids?: string[] }) {
  const { data } = await apiClient.post<ApiResponse<EvalRun>>('/ai/eval/run', payload ?? {})
  return data
}
