export type SafetyHint = {
  kind: string
  name: string
  note: string
}

export type EmergencyNumber = {
  label: string
  number: string
  notes: string | null
}

export type SafetyTips = {
  city: string | null
  tips: string[]
  nearby_hints: SafetyHint[]
  emergency_numbers: EmergencyNumber[]
  disclaimer: string
}

export type EmergencyContact = {
  id: string
  name: string
  phone: string
  relationship_label: string | null
  is_primary: boolean
}

export type EmergencyContactInput = {
  name: string
  phone: string
  relationship_label?: string
  is_primary?: boolean
}

export type SosResult = {
  ticket_id: string
  ticket_number: string
  status: string
  message: string
  is_mock: boolean
  data_notice: string
}
