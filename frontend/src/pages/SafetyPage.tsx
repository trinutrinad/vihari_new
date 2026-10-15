import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States'
import { ROUTES } from '@/constants/app'
import {
  createEmergencyContact,
  deleteEmergencyContact,
  getSafetyTips,
  listEmergencyContacts,
  triggerMockSos,
} from '@/services/safety'
import { useAuthStore } from '@/store/auth'

const CITY_PRESETS = [
  { id: 'all', label: 'General', value: undefined },
  { id: 'jaipur', label: 'Jaipur', value: 'jaipur' },
  { id: 'goa', label: 'Goa', value: 'panaji' },
  { id: 'varanasi', label: 'Varanasi', value: 'varanasi' },
  { id: 'manali', label: 'Manali', value: 'manali' },
] as const

export function SafetyPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const tokens = useAuthStore((state) => state.tokens)
  const [city, setCity] = useState<string | undefined>()
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [relation, setRelation] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [sosMessage, setSosMessage] = useState<string | null>(null)

  const tipsQuery = useQuery({
    queryKey: ['safety-tips', city ?? 'general'],
    queryFn: async () => {
      const response = await getSafetyTips(city)
      if (!response.data) throw new Error('Failed to load tips')
      return response.data
    },
  })

  const contactsQuery = useQuery({
    queryKey: ['safety-contacts'],
    queryFn: async () => {
      const response = await listEmergencyContacts()
      return response.data ?? []
    },
    enabled: Boolean(tokens?.access_token),
  })

  const addMutation = useMutation({
    mutationFn: async () => {
      if (name.trim().length < 1 || phone.trim().length < 5) {
        throw new Error('Name and phone are required')
      }
      return createEmergencyContact({
        name: name.trim(),
        phone: phone.trim(),
        relationship_label: relation.trim() || undefined,
        is_primary: (contactsQuery.data?.length ?? 0) === 0,
      })
    },
    onSuccess: async () => {
      setFormError(null)
      setName('')
      setPhone('')
      setRelation('')
      await queryClient.invalidateQueries({ queryKey: ['safety-contacts'] })
    },
    onError: (error: Error) => setFormError(error.message || 'Could not save contact'),
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => deleteEmergencyContact(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['safety-contacts'] })
    },
  })

  const sosMutation = useMutation({
    mutationFn: async () =>
      triggerMockSos({
        message: 'Mock SOS from Safety page',
        city: tipsQuery.data?.city ?? city,
      }),
    onSuccess: (response) => {
      setSosMessage(response.data?.message ?? 'Mock SOS recorded')
    },
    onError: (error: Error) => setSosMessage(error.message || 'SOS failed'),
  })

  return (
    <div className="flex flex-col gap-5 text-left">
      <div>
        <h2 className="font-display text-2xl font-semibold text-by-ink">Safety</h2>
        <p className="mt-1 text-sm text-by-muted">
          Travel tips, emergency numbers, and personal contacts. Nearby hints are unverified.
        </p>
      </div>

      <Card className="space-y-3 border-by-saffron/40 bg-by-saffron-soft/40">
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone="saffron">Real emergency</Badge>
          <p className="text-sm font-semibold text-by-ink">Dial 112</p>
        </div>
        <p className="text-sm text-by-muted">
          Mock SOS in this app does not contact police or ambulance. Use 112 for real help.
        </p>
      </Card>

      <div className="scrollbar-hide -mx-4 flex gap-2 overflow-x-auto px-4">
        {CITY_PRESETS.map((item) => (
          <Button
            key={item.id}
            size="sm"
            variant={city === item.value ? 'primary' : 'ghost'}
            onClick={() => setCity(item.value)}
          >
            {item.label}
          </Button>
        ))}
      </div>

      {tipsQuery.isLoading ? <LoadingState label="Loading safety tips…" /> : null}
      {tipsQuery.isError ? (
        <ErrorState
          title="Could not load tips"
          actionLabel="Retry"
          onAction={() => void tipsQuery.refetch()}
        />
      ) : null}

      {tipsQuery.data ? (
        <>
          <Card className="space-y-3">
            <h3 className="text-lg font-semibold text-by-ink">
              Tips{tipsQuery.data.city ? ` · ${tipsQuery.data.city}` : ''}
            </h3>
            <ul className="space-y-2">
              {tipsQuery.data.tips.map((tip) => (
                <li key={tip} className="text-sm text-by-muted">
                  • {tip}
                </li>
              ))}
            </ul>
            <p className="text-xs text-by-muted">{tipsQuery.data.disclaimer}</p>
          </Card>

          <Card className="space-y-3">
            <h3 className="text-lg font-semibold text-by-ink">Emergency numbers (India)</h3>
            <ul className="space-y-2">
              {tipsQuery.data.emergency_numbers.map((item) => (
                <li
                  key={`${item.label}-${item.number}`}
                  className="flex flex-wrap items-baseline justify-between gap-2 rounded-xl bg-by-green-soft/50 px-3 py-2"
                >
                  <div>
                    <p className="text-sm font-medium text-by-ink">{item.label}</p>
                    {item.notes ? (
                      <p className="text-xs text-by-muted">{item.notes}</p>
                    ) : null}
                  </div>
                  <a
                    href={`tel:${item.number}`}
                    className="text-sm font-semibold text-by-green hover:underline"
                  >
                    {item.number}
                  </a>
                </li>
              ))}
            </ul>
          </Card>

          {tipsQuery.data.nearby_hints.length > 0 ? (
            <Card className="space-y-3">
              <h3 className="text-lg font-semibold text-by-ink">Nearby hints (unverified)</h3>
              <ul className="space-y-2">
                {tipsQuery.data.nearby_hints.map((hint) => (
                  <li key={hint.name} className="rounded-xl border border-by-border px-3 py-2">
                    <div className="flex flex-wrap gap-2">
                      <Badge tone="neutral">{hint.kind}</Badge>
                      <p className="text-sm font-medium text-by-ink">{hint.name}</p>
                    </div>
                    <p className="mt-1 text-xs text-by-muted">{hint.note}</p>
                  </li>
                ))}
              </ul>
            </Card>
          ) : null}
        </>
      ) : null}

      <Card className="space-y-3">
        <h3 className="text-lg font-semibold text-by-ink">Personal emergency contacts</h3>
        {!tokens?.access_token ? (
          <div className="space-y-2">
            <p className="text-sm text-by-muted">Sign in to save trusted contacts on this device profile.</p>
            <Button size="sm" onClick={() => navigate(ROUTES.login)}>
              Sign in
            </Button>
          </div>
        ) : (
          <>
            {contactsQuery.isLoading ? <LoadingState label="Loading contacts…" /> : null}
            {(contactsQuery.data?.length ?? 0) === 0 && !contactsQuery.isLoading ? (
              <EmptyState
                title="No contacts yet"
                description="Add a family member or friend you can reach quickly."
              />
            ) : null}
            <ul className="space-y-2">
              {(contactsQuery.data ?? []).map((contact) => (
                <li
                  key={contact.id}
                  className="flex flex-wrap items-center justify-between gap-2 rounded-xl bg-by-green-soft/40 px-3 py-2"
                >
                  <div>
                    <p className="text-sm font-medium text-by-ink">
                      {contact.name}
                      {contact.is_primary ? ' · Primary' : ''}
                    </p>
                    <p className="text-xs text-by-muted">
                      {contact.phone}
                      {contact.relationship_label ? ` · ${contact.relationship_label}` : ''}
                    </p>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    disabled={deleteMutation.isPending}
                    onClick={() => deleteMutation.mutate(contact.id)}
                  >
                    Remove
                  </Button>
                </li>
              ))}
            </ul>
            <div className="grid gap-2 sm:grid-cols-3">
              <input
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Name"
                className="rounded-xl border border-by-border bg-white px-3 py-2 text-sm outline-none focus:border-by-green"
              />
              <input
                value={phone}
                onChange={(event) => setPhone(event.target.value)}
                placeholder="Phone"
                className="rounded-xl border border-by-border bg-white px-3 py-2 text-sm outline-none focus:border-by-green"
              />
              <input
                value={relation}
                onChange={(event) => setRelation(event.target.value)}
                placeholder="Relation (optional)"
                className="rounded-xl border border-by-border bg-white px-3 py-2 text-sm outline-none focus:border-by-green"
              />
            </div>
            <Button
              size="sm"
              variant="secondary"
              disabled={addMutation.isPending}
              onClick={() => addMutation.mutate()}
            >
              {addMutation.isPending ? 'Saving…' : 'Add contact'}
            </Button>
            {formError ? <p className="text-xs text-red-600">{formError}</p> : null}
          </>
        )}
      </Card>

      <Card className="space-y-3">
        <h3 className="text-lg font-semibold text-by-ink">Mock SOS</h3>
        <p className="text-sm text-by-muted">
          Creates a demo support ticket only. It never calls emergency services.
        </p>
        {!tokens?.access_token ? (
          <Button size="sm" variant="ghost" onClick={() => navigate(ROUTES.login)}>
            Sign in to try mock SOS
          </Button>
        ) : (
          <Button
            size="sm"
            variant="saffron"
            disabled={sosMutation.isPending}
            onClick={() => sosMutation.mutate()}
          >
            {sosMutation.isPending ? 'Recording…' : 'Trigger mock SOS'}
          </Button>
        )}
        {sosMessage ? <p className="text-xs text-by-muted">{sosMessage}</p> : null}
      </Card>
    </div>
  )
}
