import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { ErrorBoundary } from '@/components/feedback/ErrorBoundary'

function Boom(_props: Record<string, never>): never {
  throw new Error('boom-test')
}

describe('ErrorBoundary', () => {
  it('renders fallback when a child throws', () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {})
    render(
      <ErrorBoundary>
        <Boom />
      </ErrorBoundary>,
    )
    expect(screen.getByRole('heading', { name: /something went wrong/i })).toBeInTheDocument()
    expect(screen.getByText(/boom-test/i)).toBeInTheDocument()
    spy.mockRestore()
  })
})
