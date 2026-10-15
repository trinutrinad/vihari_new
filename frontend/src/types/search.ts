export type SearchResultItem = {
  id: string
  entity_type: string
  title: string
  subtitle: string | null
  slug: string | null
  category: string | null
  location_label: string | null
  rating_avg: number | null
  estimated_cost_inr: number | null
  latitude: number | null
  longitude: number | null
  distance_km: number | null
  is_seed_data: boolean
  href: string
}

export type SearchResponseData = {
  query: string
  total: number
  items: SearchResultItem[]
  facets: Record<string, number>
  page: number
  page_size: number
}

export type AutocompleteSuggestion = {
  label: string
  entity_type: string
  id: string | null
  slug: string | null
  href: string | null
}

export type TrendingSearchesData = {
  queries: string[]
  places: SearchResultItem[]
}

export const SEARCH_ENTITY_TYPES = [
  { id: 'places', label: 'Places' },
  { id: 'hotels', label: 'Hotels' },
  { id: 'restaurants', label: 'Food' },
  { id: 'temples', label: 'Temples' },
  { id: 'guides', label: 'Guides' },
  { id: 'transport', label: 'Transport' },
  { id: 'activities', label: 'Activities' },
  { id: 'cities', label: 'Cities' },
  { id: 'states', label: 'States' },
] as const
