import { Component, type ErrorInfo, type ReactNode } from 'react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'

type Props = {
  children: ReactNode
}

type State = {
  hasError: boolean
  message: string
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, message: '' }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      message: error.message || 'Unexpected application error',
    }
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error('UI error boundary', error, info.componentStack)
  }

  render() {
    if (!this.state.hasError) {
      return this.props.children
    }

    return (
      <div className="mx-auto flex min-h-svh max-w-lg items-center px-4">
        <Card className="w-full space-y-3 text-left">
          <h1 className="font-display text-2xl font-semibold text-by-ink">
            Something went wrong
          </h1>
          <p className="text-sm text-by-muted">
            The page hit an unexpected error. You can reload and continue.
          </p>
          <p className="font-mono text-xs text-by-muted">{this.state.message}</p>
          <Button
            onClick={() => {
              this.setState({ hasError: false, message: '' })
              window.location.assign('/')
            }}
          >
            Go home
          </Button>
        </Card>
      </div>
    )
  }
}
