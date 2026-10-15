import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { APP_NAME, ROUTES } from '@/constants/app'
import { registerAccount } from '@/services/auth'
import { useAuthStore } from '@/store/auth'

const schema = z.object({
  full_name: z.string().min(2),
  email: z.string().email(),
  password: z.string().min(8),
})

type FormValues = z.infer<typeof schema>

export function RegisterPage() {
  const navigate = useNavigate()
  const setSession = useAuthStore((s) => s.setSession)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { full_name: '', email: '', password: '' },
  })

  async function onSubmit(values: FormValues) {
    setLoading(true)
    setError(null)
    try {
      const response = await registerAccount(values)
      if (!response.data) throw new Error('Registration failed')
      setSession(response.data.user, response.data.tokens)
      navigate(ROUTES.profile)
    } catch {
      setError('Could not create account. Email may already be registered.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto flex min-h-svh max-w-md flex-col justify-center px-4 py-8">
      <Card className="text-left">
        <p className="font-display text-2xl font-semibold text-by-green">{APP_NAME}</p>
        <h1 className="mt-2 text-xl font-semibold text-by-ink">Create your account</h1>
        <p className="mt-1 text-sm text-by-muted">Join Bharat Yatra to save trips and preferences.</p>

        <form className="mt-4 space-y-3" onSubmit={form.handleSubmit(onSubmit)}>
          <Input label="Full name" {...form.register('full_name')} />
          <Input label="Email" type="email" {...form.register('email')} />
          <Input label="Password" type="password" {...form.register('password')} />
          {error ? <p className="text-sm text-by-danger">{error}</p> : null}
          <Button type="submit" fullWidth disabled={loading}>
            {loading ? 'Creating…' : 'Create account'}
          </Button>
        </form>

        <p className="mt-4 text-sm text-by-muted">
          Already have an account?{' '}
          <Link className="text-by-green" to={ROUTES.login}>
            Sign in
          </Link>
        </p>
      </Card>
    </div>
  )
}
