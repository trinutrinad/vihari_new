import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States'
import { ROUTES } from '@/constants/app'
import { listEvalCases, runEvalSuite } from '@/services/aiEval'
import { useAuthStore } from '@/store/auth'
import type { EvalRun } from '@/types/aiEval'

export function EvalPage() {
  const navigate = useNavigate()
  const tokens = useAuthStore((state) => state.tokens)
  const user = useAuthStore((state) => state.user)
  const [run, setRun] = useState<EvalRun | null>(null)

  const isAdmin =
    user?.primary_role === 'ADMIN' ||
    user?.primary_role === 'SUPER_ADMIN' ||
    (user?.roles ?? []).some((role) => role === 'ADMIN' || role === 'SUPER_ADMIN')

  const casesQuery = useQuery({
    queryKey: ['ai-eval-cases'],
    queryFn: async () => {
      const response = await listEvalCases()
      return response.data ?? []
    },
  })

  const runMutation = useMutation({
    mutationFn: async () => {
      const response = await runEvalSuite()
      return response.data
    },
    onSuccess: (data) => {
      if (data) setRun(data)
    },
  })

  const cases = casesQuery.data ?? []

  return (
    <div className="flex flex-col gap-5 text-left">
      <div>
        <h2 className="font-display text-2xl font-semibold text-by-ink">AI evaluation</h2>
        <p className="mt-1 text-sm text-by-muted">
          Golden-case suite for RAG grounding/refusal, planner smoke, and chat smoke.
        </p>
      </div>

      <Card className="space-y-3">
        <p className="text-sm text-by-muted">
          Run requires an admin account
          {isAdmin ? ' (you are signed in as admin).' : '.'} Demo:{' '}
          <span className="font-mono text-xs text-by-ink">demo.admin@example.com / DemoAdmin1!</span>
        </p>
        <div className="flex flex-wrap gap-2">
          {!tokens?.access_token ? (
            <Button onClick={() => navigate(ROUTES.login)}>Sign in</Button>
          ) : (
            <Button
              disabled={!isAdmin || runMutation.isPending}
              onClick={() => runMutation.mutate()}
            >
              {runMutation.isPending ? 'Running suite…' : 'Run full eval suite'}
            </Button>
          )}
          <Button variant="ghost" onClick={() => navigate(ROUTES.ask)}>
            Open Ask (RAG)
          </Button>
        </div>
        {runMutation.isError ? (
          <ErrorState title="Eval run failed. Sign in as admin and try again." />
        ) : null}
      </Card>

      {run ? (
        <Card className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-display text-lg font-semibold text-by-ink">Latest run</h3>
            <Badge tone={run.failed === 0 ? 'green' : 'saffron'}>
              {run.passed}/{run.total} passed ({Math.round(run.pass_rate * 100)}%)
            </Badge>
          </div>
          <p className="text-xs text-by-muted">{run.notice}</p>
          <p className="text-xs text-by-muted">
            Avg latency {run.metrics.avg_latency_ms ?? '—'} ms · run {run.run_id.slice(0, 8)}
          </p>
          <ul className="space-y-2">
            {run.results.map((result) => (
              <li key={result.case_id}>
                <Card className="space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <p className="font-medium text-by-ink">{result.name}</p>
                      <p className="text-xs text-by-muted">
                        {result.case_id} · {result.kind} · {result.latency_ms} ms
                      </p>
                    </div>
                    <Badge tone={result.passed ? 'green' : 'saffron'}>
                      {result.passed ? 'pass' : 'fail'}
                    </Badge>
                  </div>
                  {result.output_preview ? (
                    <p className="text-sm text-by-muted">{result.output_preview}</p>
                  ) : null}
                  <ul className="space-y-1">
                    {result.checks.map((check) => (
                      <li key={check.name} className="text-xs text-by-muted">
                        {check.passed ? '✓' : '✗'} {check.name}
                        {check.detail ? ` — ${check.detail}` : ''}
                      </li>
                    ))}
                  </ul>
                </Card>
              </li>
            ))}
          </ul>
        </Card>
      ) : null}

      <section className="space-y-3">
        <h3 className="font-display text-lg font-semibold text-by-ink">Golden cases</h3>
        {casesQuery.isLoading ? <LoadingState label="Loading cases…" /> : null}
        {casesQuery.isError ? <ErrorState title="Could not load eval cases." /> : null}
        {!casesQuery.isLoading && cases.length === 0 ? (
          <EmptyState title="No cases" description="Eval catalog is empty." />
        ) : null}
        <ul className="space-y-2">
          {cases.map((item) => (
            <li key={item.id}>
              <Card className="space-y-1">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="font-medium text-by-ink">{item.name}</p>
                  <Badge tone="neutral">{item.kind}</Badge>
                </div>
                <p className="text-sm text-by-muted">{item.description}</p>
                <p className="text-xs text-by-muted">{item.tags.join(' · ')}</p>
              </Card>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
