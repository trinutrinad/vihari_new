import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Clock3, Flame } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { SearchBar } from '@/components/ui/SearchBar'
import { EmptyState, LoadingState, ErrorState } from '@/components/feedback/States'
import { SearchResultCard } from '@/features/search/SearchResultCard'
import { ROUTES } from '@/constants/app'
import { globalSearch, searchAutocomplete, searchTrending } from '@/services/search'
import { useRecentSearchesStore } from '@/store/recentSearches'
import { SEARCH_ENTITY_TYPES } from '@/types/search'

const HYDERABAD = { lat: 17.385, lng: 78.486 }

export function SearchPage() {
  const [params, setParams] = useSearchParams()
  const navigate = useNavigate()
  const query = (params.get('q') ?? '').trim()
  const typesParam = params.get('types') ?? ''
  const state = params.get('state') ?? ''
  const minRating = params.get('min_rating')
  const maxCost = params.get('max_cost')
  const nearby = params.get('nearby') === '1'

  const selectedTypes = useMemo(
    () =>
      typesParam
        ? typesParam.split(',').map((item) => item.trim()).filter(Boolean)
        : [],
    [typesParam],
  )

  const [draftQuery, setDraftQuery] = useState(query)
  const [draftState, setDraftState] = useState(state)
  const [draftMinRating, setDraftMinRating] = useState(minRating ?? '')
  const [draftMaxCost, setDraftMaxCost] = useState(maxCost ?? '')
  const [showSuggestions, setShowSuggestions] = useState(false)
  const recent = useRecentSearchesStore((store) => store.recent)
  const addRecent = useRecentSearchesStore((store) => store.addRecent)
  const clearRecent = useRecentSearchesStore((store) => store.clearRecent)

  useEffect(() => {
    setDraftQuery(query)
    setDraftState(state)
    setDraftMinRating(minRating ?? '')
    setDraftMaxCost(maxCost ?? '')
  }, [query, state, minRating, maxCost])

  const trendingQuery = useQuery({
    queryKey: ['search-trending'],
    queryFn: async () => {
      const response = await searchTrending()
      return response.data
    },
  })

  const autocompleteQuery = useQuery({
    queryKey: ['search-autocomplete', draftQuery],
    queryFn: async () => {
      const response = await searchAutocomplete(draftQuery)
      return response.data ?? []
    },
    enabled: draftQuery.trim().length >= 2 && showSuggestions,
  })

  const searchQuery = useQuery({
    queryKey: ['global-search', query, typesParam, state, minRating, maxCost, nearby],
    queryFn: async () => {
      const response = await globalSearch({
        q: query,
        types: typesParam || undefined,
        state: state || undefined,
        min_rating: minRating ? Number(minRating) : undefined,
        max_cost: maxCost ? Number(maxCost) : undefined,
        lat: nearby ? HYDERABAD.lat : undefined,
        lng: nearby ? HYDERABAD.lng : undefined,
        radius_km: nearby ? 80 : undefined,
        page: 1,
        page_size: 30,
      })
      if (!response.data) throw new Error('Search failed')
      return response.data
    },
  })

  function commitSearch(nextQuery: string, extra?: Record<string, string | null>) {
    const cleaned = nextQuery.trim()
    const next = new URLSearchParams(params)
    if (cleaned) next.set('q', cleaned)
    else next.delete('q')
    if (extra) {
      for (const [key, value] of Object.entries(extra)) {
        if (value) next.set(key, value)
        else next.delete(key)
      }
    }
    if (cleaned) addRecent(cleaned)
    setShowSuggestions(false)
    setParams(next)
  }

  function applyDraftFilters() {
    commitSearch(query || draftQuery, {
      state: draftState.trim().toUpperCase() || null,
      min_rating: draftMinRating || null,
      max_cost: draftMaxCost || null,
    })
  }

  function toggleType(typeId: string) {
    const set = new Set(selectedTypes)
    if (set.has(typeId)) set.delete(typeId)
    else set.add(typeId)
    const value = Array.from(set).join(',')
    commitSearch(query, { types: value || null })
  }

  return (
    <div className="flex flex-col gap-5 text-left">
      <div>
        <h2 className="font-display text-2xl font-semibold text-by-ink">Search</h2>
        <p className="mt-1 text-sm text-by-muted">
          Search places, hotels, food, temples, guides, transport, activities, cities, and
          states.
        </p>
        <div className="relative mt-4">
          <SearchBar
            value={draftQuery}
            onChange={(event) => {
              setDraftQuery(event.target.value)
              setShowSuggestions(true)
            }}
            onFocus={() => setShowSuggestions(true)}
            onSubmitSearch={(value) => commitSearch(value)}
          />
          {showSuggestions && draftQuery.trim().length >= 2 ? (
            <Card className="absolute z-20 mt-2 w-full p-2 shadow-lg" padding="sm">
              {autocompleteQuery.isLoading ? (
                <p className="px-2 py-2 text-sm text-by-muted">Searching suggestions…</p>
              ) : null}
              {(autocompleteQuery.data ?? []).map((suggestion) => (
                <button
                  key={`${suggestion.entity_type}-${suggestion.label}`}
                  type="button"
                  className="flex w-full items-center justify-between rounded-xl px-3 py-2 text-left text-sm hover:bg-by-green-soft"
                  onClick={() => {
                    if (suggestion.href?.startsWith('/places/')) {
                      addRecent(suggestion.label)
                      navigate(suggestion.href)
                      return
                    }
                    commitSearch(suggestion.label)
                  }}
                >
                  <span className="font-medium text-by-ink">{suggestion.label}</span>
                  <Badge tone="neutral">{suggestion.entity_type}</Badge>
                </button>
              ))}
              {!autocompleteQuery.isLoading && (autocompleteQuery.data?.length ?? 0) === 0 ? (
                <p className="px-2 py-2 text-sm text-by-muted">No suggestions</p>
              ) : null}
            </Card>
          ) : null}
        </div>
      </div>

      <section className="space-y-3">
        <h3 className="text-sm font-semibold text-by-ink">Filters</h3>
        <div className="scrollbar-hide -mx-4 flex gap-2 overflow-x-auto px-4">
          {SEARCH_ENTITY_TYPES.map((type) => (
            <Button
              key={type.id}
              size="sm"
              variant={selectedTypes.includes(type.id) ? 'primary' : 'ghost'}
              onClick={() => toggleType(type.id)}
            >
              {type.label}
            </Button>
          ))}
        </div>
        <div className="grid gap-3 sm:grid-cols-3">
          <Input
            label="State code"
            placeholder="TG, KA, RJ…"
            value={draftState}
            onChange={(event) => setDraftState(event.target.value)}
          />
          <Input
            label="Min rating"
            type="number"
            min={0}
            max={5}
            step={0.5}
            value={draftMinRating}
            onChange={(event) => setDraftMinRating(event.target.value)}
          />
          <Input
            label="Max budget (₹)"
            type="number"
            min={0}
            value={draftMaxCost}
            onChange={(event) => setDraftMaxCost(event.target.value)}
          />
        </div>
        <div className="flex flex-wrap gap-2">
          <Button size="sm" onClick={applyDraftFilters}>
            Apply filters
          </Button>
          <Button
            size="sm"
            variant={nearby ? 'saffron' : 'ghost'}
            onClick={() => commitSearch(query, { nearby: nearby ? null : '1' })}
          >
            Near Hyderabad (demo)
          </Button>
        </div>
      </section>

      {!query && recent.length > 0 ? (
        <Card className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="flex items-center gap-2 text-sm font-semibold text-by-ink">
              <Clock3 className="size-4" aria-hidden /> Recent searches
            </h3>
            <button
              type="button"
              className="text-xs text-by-muted hover:text-by-danger"
              onClick={clearRecent}
            >
              Clear
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {recent.map((item) => (
              <button
                key={item}
                type="button"
                className="rounded-full border border-by-border bg-white px-3 py-1.5 text-sm"
                onClick={() => commitSearch(item)}
              >
                {item}
              </button>
            ))}
          </div>
        </Card>
      ) : null}

      {!query ? (
        <Card className="space-y-3">
          <h3 className="flex items-center gap-2 text-sm font-semibold text-by-ink">
            <Flame className="size-4 text-by-saffron" aria-hidden /> Trending searches
          </h3>
          {trendingQuery.isLoading ? <LoadingState label="Loading trends…" /> : null}
          <div className="flex flex-wrap gap-2">
            {(trendingQuery.data?.queries ?? []).map((item) => (
              <button
                key={item}
                type="button"
                className="rounded-full bg-by-saffron-soft px-3 py-1.5 text-sm font-medium text-by-saffron"
                onClick={() => commitSearch(item)}
              >
                {item}
              </button>
            ))}
          </div>
          {(trendingQuery.data?.places?.length ?? 0) > 0 ? (
            <div className="grid gap-3 pt-2">
              {trendingQuery.data?.places.map((place) => (
                <SearchResultCard
                  key={String(place.id)}
                  item={place}
                  onSelect={(item) => navigate(item.href)}
                />
              ))}
            </div>
          ) : null}
        </Card>
      ) : null}

      {searchQuery.isLoading ? <LoadingState label="Searching Bharat Yatra…" /> : null}
      {searchQuery.isError ? (
        <ErrorState
          title="Search unavailable"
          description="Start the API and seed data, then retry."
          actionLabel="Retry"
          onAction={() => void searchQuery.refetch()}
        />
      ) : null}

      {searchQuery.data ? (
        <>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-sm text-by-muted">
              {searchQuery.data.total} result{searchQuery.data.total === 1 ? '' : 's'}
              {query ? ` for “${query}”` : ''}
            </p>
            <div className="flex flex-wrap gap-2">
              {Object.entries(searchQuery.data.facets).map(([type, count]) => (
                <Badge key={type} tone="green">
                  {type}: {count}
                </Badge>
              ))}
            </div>
          </div>

          {searchQuery.data.items.length === 0 ? (
            <Card>
              <EmptyState
                title="No matches"
                description="Try another query, clear filters, or browse trending searches."
                actionLabel="Clear filters"
                onAction={() => {
                  const next = new URLSearchParams()
                  if (query) next.set('q', query)
                  setParams(next)
                }}
              />
            </Card>
          ) : (
            <div className="grid gap-3">
              {searchQuery.data.items.map((item) => (
                <SearchResultCard
                  key={`${item.entity_type}-${item.id}`}
                  item={item}
                  onSelect={(selected) => navigate(selected.href)}
                />
              ))}
            </div>
          )}
        </>
      ) : null}

      <Link to={ROUTES.home} className="text-sm font-medium text-by-green hover:underline">
        ← Back to Home
      </Link>
    </div>
  )
}
