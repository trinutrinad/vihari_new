import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States'
import { listRagDocuments, queryRag, seedRagDemo } from '@/services/rag'
import type { RagQueryResult } from '@/types/rag'

const SUGGESTIONS = [
  'What should I pack for monsoon travel in India?',
  'Temple visit etiquette basics',
  'Are Bharat Yatra bookings real charges?',
  'Family-friendly trip planning tips',
  'What emergency number should I dial in India?',
]

export function AskPage() {
  const queryClient = useQueryClient()
  const [question, setQuestion] = useState(SUGGESTIONS[0])
  const [result, setResult] = useState<RagQueryResult | null>(null)

  const docsQuery = useQuery({
    queryKey: ['rag-documents'],
    queryFn: async () => {
      const response = await listRagDocuments({ limit: 20 })
      return response.data ?? []
    },
  })

  const askMutation = useMutation({
    mutationFn: async () => {
      const response = await queryRag({ question: question.trim(), top_k: 4 })
      return response.data
    },
    onSuccess: (data) => {
      if (data) setResult(data)
    },
  })

  const seedMutation = useMutation({
    mutationFn: async () => seedRagDemo(),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['rag-documents'] })
    },
  })

  const documents = docsQuery.data ?? []

  return (
    <div className="flex flex-col gap-5 text-left">
      <div>
        <h2 className="font-display text-2xl font-semibold text-by-ink">Ask (RAG)</h2>
        <p className="mt-1 text-sm text-by-muted">
          Grounded answers from curated seed knowledge — with source citations.
        </p>
      </div>

      <Card className="space-y-3">
        <Input
          label="Question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          hint="Answers require retrieved sources; otherwise we say we could not verify."
        />
        <div className="flex flex-wrap gap-2">
          {SUGGESTIONS.map((item) => (
            <button
              key={item}
              type="button"
              className="rounded-full border border-by-border px-3 py-1 text-xs text-by-muted hover:border-by-green hover:text-by-green"
              onClick={() => setQuestion(item)}
            >
              {item}
            </button>
          ))}
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            disabled={!question.trim() || askMutation.isPending}
            onClick={() => askMutation.mutate()}
          >
            {askMutation.isPending ? 'Retrieving…' : 'Ask with sources'}
          </Button>
          <Button
            variant="ghost"
            disabled={seedMutation.isPending}
            onClick={() => seedMutation.mutate()}
          >
            {seedMutation.isPending ? 'Seeding…' : 'Seed demo corpus'}
          </Button>
        </div>
        {askMutation.isError ? <ErrorState title="Could not run RAG query." /> : null}
      </Card>

      {result ? (
        <Card className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-display text-lg font-semibold text-by-ink">Answer</h3>
            <Badge tone={result.verified ? 'green' : 'saffron'}>
              {result.verified ? 'grounded' : 'unverified'}
            </Badge>
          </div>
          <p className="text-sm leading-relaxed text-by-ink">{result.answer}</p>
          <p className="text-xs text-by-muted">{result.notice}</p>
          <p className="text-xs text-by-muted">
            Model {result.model} · embeddings {result.embedding_model}
          </p>
          {result.sources.length > 0 ? (
            <ul className="space-y-2">
              {result.sources.map((source, index) => (
                <li key={`${source.document_id}-${source.chunk_index}`}>
                  <Card className="space-y-1">
                    <p className="text-sm font-medium text-by-ink">
                      [{index + 1}] {source.title}
                    </p>
                    <p className="text-xs uppercase tracking-wide text-by-muted">
                      {source.source_type} · score {source.score.toFixed(3)}
                    </p>
                    <p className="text-sm text-by-muted">{source.excerpt}</p>
                  </Card>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState
              title="No sources cited"
              description="Try a suggestion about monsoon, temples, bookings, or emergencies."
            />
          )}
        </Card>
      ) : null}

      <section className="space-y-3">
        <h3 className="font-display text-lg font-semibold text-by-ink">Knowledge documents</h3>
        {docsQuery.isLoading ? <LoadingState label="Loading documents…" /> : null}
        {docsQuery.isError ? <ErrorState title="Could not load documents." /> : null}
        {!docsQuery.isLoading && documents.length === 0 ? (
          <EmptyState
            title="No documents yet"
            description="Click Seed demo corpus, or run backend seed."
          />
        ) : null}
        <ul className="space-y-2">
          {documents.map((doc) => (
            <li key={doc.id}>
              <Card className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <p className="font-medium text-by-ink">{doc.title}</p>
                  <p className="text-xs text-by-muted">
                    {doc.source_type} · {doc.chunk_count} chunks
                  </p>
                </div>
                <Badge tone="neutral">{doc.language}</Badge>
              </Card>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
