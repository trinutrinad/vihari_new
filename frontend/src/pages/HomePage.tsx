import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { PlaceCard, type PlaceCardModel } from '@/components/ui/PlaceCard'
import { SearchBar } from '@/components/ui/SearchBar'
import { Badge } from '@/components/ui/Badge'
import { APP_TAGLINE, ROUTES } from '@/constants/app'
import {
  HOME_CATEGORIES,
  HOME_PLACES,
  placesByCategory,
  placesByTag,
} from '@/constants/home'
import { AiPlannerBanner } from '@/features/home/AiPlannerBanner'
import { CategoryScroller } from '@/features/home/CategoryScroller'
import { HorizontalSection } from '@/features/home/HorizontalSection'
import type { HomeCategory } from '@/types/place'
import { listPlaces } from '@/services/places'
import { apiPlaceToCard, homePlaceToCard } from '@/utils/placeCards'

const SECTION_DEFS = [
  {
    id: 'popular',
    title: 'Popular destinations',
    subtitle: 'Traveller favourites across India',
    getPlaces: () => placesByTag('popular'),
    api: { featured: true as const },
  },
  {
    id: 'nearby',
    title: 'Nearby places',
    subtitle: 'Based on a demo Hyderabad location',
    getPlaces: () => placesByTag('nearby'),
    api: { lat: 17.385, lng: 78.486 },
  },
  {
    id: 'weekend',
    title: 'Weekend getaways',
    subtitle: 'Short escapes for Friday–Sunday',
    getPlaces: () => placesByTag('weekend'),
    api: { featured: true as const },
  },
  {
    id: 'temples',
    title: 'Temples',
    subtitle: 'Pilgrimage-friendly areas (demo listings)',
    getPlaces: () => placesByCategory('Temples'),
    api: { category: 'temple' },
  },
  {
    id: 'beaches',
    title: 'Beaches',
    subtitle: 'Coastal walks and seafront evenings',
    getPlaces: () => placesByCategory('Beaches'),
    api: { category: 'beach' },
  },
  {
    id: 'mountains',
    title: 'Mountains',
    subtitle: 'Hill stations and high meadows',
    getPlaces: () => placesByCategory('Mountains'),
    api: { category: 'mountain' },
  },
  {
    id: 'waterfalls',
    title: 'Waterfalls',
    subtitle: 'Nature lookouts and monsoon favourites',
    getPlaces: () => placesByTag('waterfall'),
    api: { category: 'waterfall' },
  },
  {
    id: 'historical',
    title: 'Historical places',
    subtitle: 'Forts, ruins, and heritage circuits',
    getPlaces: () => placesByCategory('Historical'),
    api: { category: 'historical' },
  },
  {
    id: 'wildlife',
    title: 'Wildlife',
    subtitle: 'Forest edges and safari gateways',
    getPlaces: () => placesByTag('wildlife'),
    api: { category: 'wildlife' },
  },
  {
    id: 'adventure',
    title: 'Adventure',
    subtitle: 'Treks, rivers, and outdoor energy',
    getPlaces: () => placesByTag('adventure'),
    api: { category: 'adventure' },
  },
  {
    id: 'food',
    title: 'Food experiences',
    subtitle: 'Regional flavours worth a detour',
    getPlaces: () => placesByTag('food'),
    api: { category: 'food' },
  },
  {
    id: 'hidden',
    title: 'Hidden gems',
    subtitle: 'Quieter picks beyond the usual list',
    getPlaces: () => placesByTag('hidden'),
    api: { hidden_gem: true as const },
  },
  {
    id: 'budget',
    title: 'Budget trips',
    subtitle: 'Lower estimated day costs',
    getPlaces: () => placesByTag('budget'),
    api: {},
  },
  {
    id: 'roadtrips',
    title: 'Road trips',
    subtitle: 'Scenic drives and stopover towns',
    getPlaces: () => placesByTag('roadtrip'),
    api: {},
  },
  {
    id: 'trending',
    title: 'Trending now',
    subtitle: 'What travellers are exploring this week',
    getPlaces: () => placesByTag('trending'),
    api: { featured: true as const },
  },
  {
    id: 'recommended',
    title: 'Recommended for you',
    subtitle: 'Based on common first-time India preferences',
    getPlaces: () => placesByTag('recommended'),
    api: { family_friendly: true as const },
  },
] as const

export function HomePage() {
  const navigate = useNavigate()
  const [activeCategory, setActiveCategory] = useState<string | null>(null)

  const apiPlacesQuery = useQuery({
    queryKey: ['home-places'],
    queryFn: async () => {
      const response = await listPlaces({ page: 1, page_size: 50 })
      return response.data?.items ?? []
    },
    retry: 1,
  })

  const filteredSections = useMemo(() => {
    if (!activeCategory) return SECTION_DEFS
    const category = HOME_CATEGORIES.find((item) => item.id === activeCategory)
    if (!category) return SECTION_DEFS
    return SECTION_DEFS.filter(
      (section) =>
        section.id === category.id ||
        section.id === 'popular' ||
        section.id === 'recommended',
    )
  }, [activeCategory])

  function handleSearch(value: string) {
    const next = value.trim()
    navigate(next ? `${ROUTES.search}?q=${encodeURIComponent(next)}` : ROUTES.search)
  }

  function handleCategory(category: HomeCategory) {
    setActiveCategory((current) => (current === category.id ? null : category.id))
    document.getElementById(category.id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  function sectionCards(section: (typeof SECTION_DEFS)[number]): PlaceCardModel[] {
    const apiItems = apiPlacesQuery.data
    if (apiItems && apiItems.length > 0) {
      const api = section.api as {
        category?: string
        featured?: boolean
        hidden_gem?: boolean
        lat?: number
        lng?: number
      }
      if (api.category) {
        return apiItems
          .filter((item) => item.category?.slug === api.category)
          .slice(0, 8)
          .map(apiPlaceToCard)
      }
      if (api.featured) {
        return apiItems.filter((item) => item.is_featured).slice(0, 8).map(apiPlaceToCard)
      }
      if (api.hidden_gem) {
        return apiItems.filter((item) => item.is_hidden_gem).slice(0, 8).map(apiPlaceToCard)
      }
      if (api.lat != null) {
        return apiItems
          .filter((item) => item.city_name === 'Hyderabad' || item.city_name === 'Visakhapatnam')
          .slice(0, 8)
          .map(apiPlaceToCard)
      }
      return apiItems.slice(0, 8).map(apiPlaceToCard)
    }
    return section.getPlaces().map(homePlaceToCard)
  }

  return (
    <div className="flex flex-col gap-8">
      <section className="animate-fade-up text-left">
        <Badge tone="saffron">
          {apiPlacesQuery.isSuccess ? 'Live seed places' : 'Demo destinations · offline fallback'}
        </Badge>
        <h2 className="mt-3 font-display text-3xl font-semibold leading-tight text-by-ink sm:text-4xl">
          Where do you want to go?
        </h2>
        <p className="mt-2 max-w-xl text-sm text-by-muted sm:text-base">{APP_TAGLINE}</p>
        <div className="mt-4">
          <SearchBar onSubmitSearch={handleSearch} />
        </div>
        <p className="mt-2 text-xs text-by-muted">
          Try “temples near Vizag”, “weekend from Hyderabad”, or “Goa beaches”
        </p>
      </section>

      <section className="text-left">
        <div className="mb-3 flex items-end justify-between gap-2 px-0">
          <h3 className="text-lg font-semibold text-by-ink">Categories</h3>
          <span className="text-xs text-by-muted">
            {apiPlacesQuery.data?.length ?? HOME_PLACES.length} places
          </span>
        </div>
        <CategoryScroller
          categories={HOME_CATEGORIES}
          activeId={activeCategory}
          onSelect={handleCategory}
        />
      </section>

      <AiPlannerBanner onPlan={() => navigate(ROUTES.planner)} />

      {filteredSections.map((section) => {
        const places = sectionCards(section)
        if (places.length === 0) return null
        return (
          <HorizontalSection
            key={section.id}
            id={section.id}
            title={section.title}
            subtitle={section.subtitle}
            action={
              <button
                type="button"
                className="text-sm font-medium text-by-green hover:underline"
                onClick={() => {
                  const api = section.api as { category?: string }
                  navigate(
                    `${ROUTES.explore}${api.category ? `?category=${api.category}` : ''}`,
                  )
                }}
              >
                See all
              </button>
            }
          >
            {places.map((place) => (
              <div key={`${section.id}-${place.id}`} className="snap-start">
                <PlaceCard
                  place={place}
                  onSelect={(selected) => navigate(`/places/${selected.id}`)}
                />
              </div>
            ))}
          </HorizontalSection>
        )
      })}
    </div>
  )
}
