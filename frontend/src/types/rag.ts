export type RagSource = {
  document_id: string
  title: string
  source_type: string
  source_uri: string | null
  chunk_index: number
  excerpt: string
  score: number
}

export type RagQueryResult = {
  answer: string
  verified: boolean
  sources: RagSource[]
  model: string
  embedding_model: string
  notice: string
}

export type RagDocument = {
  id: string
  title: string
  source_type: string
  source_uri: string | null
  language: string
  chunk_count: number
  created_at: string | null
}
