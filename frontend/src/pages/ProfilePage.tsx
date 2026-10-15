import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { ROUTES } from '@/constants/app'
import { fetchMe, logoutAccount, updateProfile } from '@/services/auth'
import { useAuthStore } from '@/store/auth'

export function ProfilePage() {
  const navigate = useNavigate()
  const { user, tokens, setUser, setSession, clearSession } = useAuthStore()
  const [homeCity, setHomeCity] = useState(user?.profile?.home_city ?? '')
  const [language, setLanguage] = useState(user?.profile?.preferred_language ?? 'en')
  const [bio, setBio] = useState(user?.profile?.bio ?? '')
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!tokens?.access_token) return
    void fetchMe()
      .then((response) => {
        if (response.data) setUser(response.data)
      })
      .catch(() => {
        clearSession()
      })
  }, [tokens?.access_token, setUser, clearSession])

  if (!user) {
    return (
      <Card className="text-left">
        <h2 className="font-display text-2xl font-semibold text-by-ink">Profile</h2>
        <p className="mt-2 text-sm text-by-muted">
          Sign in to manage preferences, saved places, and bookings.
        </p>
        <div className="mt-4 flex gap-2">
          <Button onClick={() => navigate(ROUTES.login)}>Sign in</Button>
          <Button variant="ghost" onClick={() => navigate(ROUTES.register)}>
            Create account
          </Button>
        </div>
      </Card>
    )
  }

  async function onSave() {
    setError(null)
    try {
      const response = await updateProfile({
        home_city: homeCity,
        preferred_language: language,
        bio,
      })
      if (response.data && tokens) {
        setSession(response.data, tokens)
        setMessage('Profile saved')
      }
    } catch {
      setError('Could not save profile')
    }
  }

  async function onLogout() {
    try {
      await logoutAccount(tokens?.refresh_token)
    } finally {
      clearSession()
      navigate(ROUTES.login)
    }
  }

  return (
    <div className="space-y-4">
      <Card className="text-left">
        <h2 className="font-display text-2xl font-semibold text-by-ink">{user.full_name}</h2>
        <p className="mt-1 text-sm text-by-muted">{user.email ?? user.phone}</p>
        <p className="mt-2 text-xs uppercase tracking-wide text-by-green">{user.primary_role}</p>
        <Link
          className="mt-3 inline-block text-sm font-medium text-by-green hover:underline"
          to={ROUTES.business}
        >
          Open business dashboard
        </Link>
        <Link
          className="mt-2 ml-4 inline-block text-sm font-medium text-by-blue hover:underline"
          to={ROUTES.admin}
        >
          Open admin dashboard
        </Link>
        <Link
          className="mt-2 ml-4 inline-block text-sm font-medium text-by-blue hover:underline"
          to={ROUTES.eval}
        >
          Open AI evaluation
        </Link>
      </Card>

      <Card className="space-y-3 text-left">
        <h3 className="text-lg font-semibold text-by-ink">Travel preferences</h3>
        <Input label="Home city" value={homeCity} onChange={(e) => setHomeCity(e.target.value)} />
        <Input
          label="Language"
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          hint="en, hi, te, ta, kn, ml, mr, bn, gu, or"
        />
        <Input label="Bio" value={bio} onChange={(e) => setBio(e.target.value)} />
        {message ? <p className="text-sm text-by-green">{message}</p> : null}
        {error ? <p className="text-sm text-by-danger">{error}</p> : null}
        <div className="flex flex-wrap gap-2">
          <Button onClick={() => void onSave()}>Save</Button>
          <Button variant="ghost" onClick={() => void onLogout()}>
            Log out
          </Button>
          <Link className="self-center text-sm text-by-blue" to={ROUTES.home}>
            Back to home
          </Link>
        </div>
      </Card>
    </div>
  )
}
