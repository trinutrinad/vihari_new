import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { LoadingState, ErrorState } from '@/components/feedback/States'
import { getHealth, getReadiness } from '@/services/health'

export function HealthPage() {
  const liveQuery = useQuery({
    queryKey: ['health'],
    queryFn: getHealth,
  })

  const readyQuery = useQuery({
    queryKey: ['health-ready'],
    queryFn: getReadiness,
    retry: false,
  })

  if (liveQuery.isLoading) {
    return <LoadingState label="Checking API health…" />
  }

  if (liveQuery.isError || !liveQuery.data) {
    return (
      <ErrorState
        title="API unreachable"
        description="Start the backend on port 8000, then retry."
        actionLabel="Retry"
        onAction={() => {
          void liveQuery.refetch()
          void readyQuery.refetch()
        }}
      />
    )
  }

  const live = liveQuery.data.data
  const ready = readyQuery.data?.data
  const readyOk = readyQuery.isSuccess && ready?.status === 'ready'

  return (
    <div className="flex flex-col gap-4 text-left">
      <Card>
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="font-display text-2xl font-semibold text-by-ink">System health</h2>
          <Badge tone={live?.status === 'healthy' ? 'green' : 'saffron'}>
            liveness: {live?.status ?? 'unknown'}
          </Badge>
          <Badge tone={readyOk ? 'green' : 'saffron'}>
            readiness: {ready?.status ?? (readyQuery.isLoading ? 'checking' : 'unavailable')}
          </Badge>
        </div>
        <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-by-muted">Service</dt>
            <dd className="font-medium text-by-ink">{live?.service}</dd>
          </div>
          <div>
            <dt className="text-by-muted">Environment</dt>
            <dd className="font-medium text-by-ink">{live?.environment}</dd>
          </div>
          <div>
            <dt className="text-by-muted">Version</dt>
            <dd className="font-medium text-by-ink">{live?.version}</dd>
          </div>
          <div>
            <dt className="text-by-muted">Timestamp</dt>
            <dd className="font-medium text-by-ink">{live?.timestamp}</dd>
          </div>
        </dl>
      </Card>

      <Card className="space-y-2">
        <h3 className="font-display text-lg font-semibold text-by-ink">Dependency checks</h3>
        <p className="text-xs text-by-muted">
          Readiness requires database. Redis is reported as a soft dependency.
        </p>
        {readyQuery.isError ? (
          <p className="text-sm text-by-danger">Readiness probe failed or returned 503.</p>
        ) : null}
        <ul className="space-y-1 text-sm">
          {Object.entries(ready?.checks ?? live?.checks ?? {}).map(([name, value]) => (
            <li key={name} className="flex justify-between gap-3">
              <span className="text-by-muted">{name}</span>
              <span className="font-mono text-xs text-by-ink">{value}</span>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  )
}
