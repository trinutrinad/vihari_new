import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { APP_NAME, ROUTES } from '@/constants/app'
import { forgotPassword, resetPassword } from '@/services/auth'

const emailSchema = z.object({ email: z.string().email() })
const resetSchema = z.object({
  token: z.string().min(10),
  new_password: z.string().min(8),
})

type EmailForm = z.infer<typeof emailSchema>
type ResetForm = z.infer<typeof resetSchema>

export function ForgotPasswordPage() {
  const [message, setMessage] = useState<string | null>(null)
  const [devToken, setDevToken] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const emailForm = useForm<EmailForm>({
    resolver: zodResolver(emailSchema),
    defaultValues: { email: '' },
  })
  const resetForm = useForm<ResetForm>({
    resolver: zodResolver(resetSchema),
    defaultValues: { token: '', new_password: '' },
  })

  async function onForgot(values: EmailForm) {
    setError(null)
    try {
      const response = await forgotPassword(values.email)
      setMessage(response.data?.message ?? response.message)
      if (response.data?.reset_token) {
        setDevToken(response.data.reset_token)
        resetForm.setValue('token', response.data.reset_token)
      }
    } catch {
      setError('Could not start password reset')
    }
  }

  async function onReset(values: ResetForm) {
    setError(null)
    try {
      await resetPassword(values.token, values.new_password)
      setMessage('Password updated. You can sign in with the new password.')
      setDevToken(null)
    } catch {
      setError('Reset failed. Token may be invalid or expired.')
    }
  }

  return (
    <div className="mx-auto flex min-h-svh max-w-md flex-col justify-center px-4 py-8">
      <Card className="text-left">
        <p className="font-display text-2xl font-semibold text-by-green">{APP_NAME}</p>
        <h1 className="mt-2 text-xl font-semibold text-by-ink">Forgot password</h1>
        <p className="mt-1 text-sm text-by-muted">
          We will issue a reset token. In production this is emailed; in debug it may appear below.
        </p>

        <form className="mt-4 space-y-3" onSubmit={emailForm.handleSubmit(onForgot)}>
          <Input label="Email" type="email" {...emailForm.register('email')} />
          <Button type="submit" fullWidth>
            Send reset link
          </Button>
        </form>

        {(devToken || message) && (
          <form className="mt-6 space-y-3 border-t border-by-border pt-4" onSubmit={resetForm.handleSubmit(onReset)}>
            <Input label="Reset token" {...resetForm.register('token')} />
            <Input label="New password" type="password" {...resetForm.register('new_password')} />
            <Button type="submit" variant="secondary" fullWidth>
              Update password
            </Button>
          </form>
        )}

        {message ? <p className="mt-3 text-sm text-by-green">{message}</p> : null}
        {error ? <p className="mt-3 text-sm text-by-danger">{error}</p> : null}

        <Link className="mt-4 inline-block text-sm text-by-blue" to={ROUTES.login}>
          Back to sign in
        </Link>
      </Card>
    </div>
  )
}
