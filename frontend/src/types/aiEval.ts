export type EvalKind = 'rag_grounded' | 'rag_refusal' | 'planner_smoke' | 'chat_smoke'

export type EvalCase = {
  id: string
  name: string
  kind: EvalKind
  description: string
  tags: string[]
}

export type EvalCheck = {
  name: string
  passed: boolean
  detail: string
}

export type EvalCaseResult = {
  case_id: string
  name: string
  kind: EvalKind
  passed: boolean
  latency_ms: number
  checks: EvalCheck[]
  output_preview: string | null
  error: string | null
}

export type EvalRun = {
  run_id: string
  started_at: string
  finished_at: string
  total: number
  passed: number
  failed: number
  pass_rate: number
  results: EvalCaseResult[]
  metrics: {
    by_kind?: Record<string, { passed: number; failed: number }>
    avg_latency_ms?: number
  }
  notice: string
}
