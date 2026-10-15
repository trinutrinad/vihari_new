export type PlannedStop = {
  place_id: string | null
  title: string
  time_slot: string | null
  estimated_cost_inr: number | null
  city: string | null
  is_seed_data: boolean
}

export type PlannedDay = {
  day_number: number
  title: string
  notes: string | null
  places: PlannedStop[]
}

export type PlanSuggestion = {
  id: string
  name: string
  starting_price_inr?: number | null
  cuisine_tags?: string | null
  rating_avg?: number | null
  languages?: string | null
  specialization?: string | null
  price_per_day_inr?: number | null
  code?: string | null
  vehicle_type?: string | null
  base_fare_inr?: number | null
  per_km_inr?: number | null
  is_seed_data: boolean
}

export type ToolTrace = {
  name: string
  ok: boolean
  message: string
  provenance: string
}

export type AgentTrace = {
  agent: string
  ok: boolean
  summary: string
  tools_used: string[]
}

export type AgentInfo = {
  name: string
  role: string
  status: string
}

export type WeatherOutlook = {
  city: string
  days: Array<{
    day: number
    summary: string
    temp_c_high: number
    temp_c_low: number
  }>
  disclaimer: string
}

export type SafetyOutlook = {
  city: string
  tips: string[]
  nearby_hints: Array<{ kind: string; name: string; note: string }>
  disclaimer: string
}

export type BookingStatus = {
  available: boolean
  message: string
  suggested_next: string[]
}

export type PlanTripResult = {
  title: string
  summary: string
  origin_city: string
  destination_summary: string
  days: PlannedDay[]
  hotels: PlanSuggestion[]
  restaurants: PlanSuggestion[]
  guides?: PlanSuggestion[]
  transport?: PlanSuggestion[]
  weather?: WeatherOutlook | null
  safety?: SafetyOutlook | null
  booking?: BookingStatus | null
  budget_inr: number | null
  estimated_cost_inr: number | null
  budget_note: string | null
  cost_breakdown?: Record<string, number> | null
  provider: string
  model: string
  prompt_tokens: number
  completion_tokens: number
  tool_trace: ToolTrace[]
  agent_trace?: AgentTrace[]
  notice: string
  conversation_id: string | null
  trip: {
    id: string
    title: string
    is_ai_generated: boolean
  } | null
}

export type PlanTripPayload = {
  origin_city: string
  days: number
  budget_inr?: number
  interests?: string[]
  travelers?: number
  destination_hint?: string
  prompt?: string
  save?: boolean
}

export type ChatResult = {
  conversation_id: string
  reply: string
  provider: string
  model: string
  prompt_tokens: number
  completion_tokens: number
  notice: string
}
