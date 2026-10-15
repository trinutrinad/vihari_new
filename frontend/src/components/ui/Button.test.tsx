import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Button } from '@/components/ui/Button'

describe('Button', () => {
  it('renders label', () => {
    render(<Button>Plan trip</Button>)
    expect(screen.getByRole('button', { name: /plan trip/i })).toBeInTheDocument()
  })
})
