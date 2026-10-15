import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { APP_NAME, ROUTES } from '@/constants/app'
import { loginAccount, requestPhoneOtp, verifyPhoneOtp } from '@/services/auth'
import { useAuthStore } from '@/store/auth'

const passwordSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
})

type PasswordForm = z.infer<typeof passwordSchema>

export function LoginPage() {
  const navigate = useNavigate()
  const setSession = useAuthStore((s) => s.setSession)
  const [mode, setMode] = useState<'password' | 'otp'>('password')
  const [error, setError] = useState<string | null>(null)
  const [phone, setPhone] = useState('')
  const [otpCode, setOtpCode] = useState('')
  const [challengeId, setChallengeId] = useState<string | null>(null)
  const [debugCode, setDebugCode] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const form = useForm<PasswordForm>({
    resolver: zodResolver(passwordSchema),
    defaultValues: { email: '', password: '' },
  })

  async function onPasswordSubmit(values: PasswordForm) {
    setLoading(true)
    setError(null)
    try {
      const response = await loginAccount(values)
      if (!response.data) throw new Error('Login failed')
      setSession(response.data.user, response.data.tokens)
      navigate(ROUTES.profile)
    } catch {
      setError('Invalid email or password')
    } finally {
      setLoading(false)
    }
  }

  async function onRequestOtp() {
    setLoading(true)
    setError(null)
    try {
      const response = await requestPhoneOtp(phone)
      if (!response.data) throw new Error('OTP request failed')
      setChallengeId(response.data.challenge_id)
      setDebugCode(response.data.debug_code ?? null)
    } catch {
      setError('Could not send OTP')
    } finally {
      setLoading(false)
    }
  }

  async function onVerifyOtp() {
    if (!challengeId) return
    setLoading(true)
    setError(null)
    try {
      const response = await verifyPhoneOtp({
        challenge_id: challengeId,
        code: otpCode,
      })
      if (!response.data) throw new Error('OTP verify failed')
      setSession(response.data.user, response.data.tokens)
      navigate(ROUTES.profile)
    } catch {
      setError('Invalid OTP')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto flex min-h-svh max-w-md flex-col justify-center px-4 py-8">
      <Card className="text-left">
        <p className="font-display text-2xl font-semibold text-by-green">{APP_NAME}</p>
        <h1 className="mt-2 text-xl font-semibold text-by-ink">Welcome back</h1>
        <p className="mt-1 text-sm text-by-muted">Sign in to continue your journey.</p>

        <div className="mt-4 flex gap-2">
          <Button
            variant={mode === 'password' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setMode('password')}
          >
            Email
          </Button>
          <Button
            variant={mode === 'otp' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setMode('otp')}
          >
            Phone OTP
          </Button>
        </div>

        {mode === 'password' ? (
          <form className="mt-4 space-y-3" onSubmit={form.handleSubmit(onPasswordSubmit)}>
            <Input label="Email" type="email" {...form.register('email')} />
            <Input label="Password" type="password" {...form.register('password')} />
            {error ? <p className="text-sm text-by-danger">{error}</p> : null}
            <Button type="submit" fullWidth disabled={loading}>
              {loading ? 'Signing in…' : 'Sign in'}
            </Button>
            <p className="text-xs text-by-muted">
              Demo owner: demo.owner@example.com / DemoOwner1!
              <br />
              Demo admin: demo.admin@example.com / DemoAdmin1!
            </p>
          </form>
        ) : (
          <div className="mt-4 space-y-3">
            <Input
              label="Phone"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+9198XXXXXXXX"
            />
            {!challengeId ? (
              <Button fullWidth disabled={loading || phone.length < 10} onClick={() => void onRequestOtp()}>
                Send OTP
              </Button>
            ) : (
              <>
                <Input
                  label="OTP"
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value)}
                  hint={debugCode ? `Mock OTP (dev): ${debugCode}` : undefined}
                />
                <Button fullWidth disabled={loading || otpCode.length < 4} onClick={() => void onVerifyOtp()}>
                  Verify & sign in
                </Button>
              </>
            )}
            {error ? <p className="text-sm text-by-danger">{error}</p> : null}
          </div>
        )}

        <div className="mt-4 flex justify-between text-sm">
          <Link className="text-by-blue" to={ROUTES.forgotPassword}>
            Forgot password?
          </Link>
          <Link className="text-by-green" to={ROUTES.register}>
            Create account
          </Link>
        </div>
      </Card>
    </div>
  )
}
