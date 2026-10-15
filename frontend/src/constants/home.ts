import type { HomeCategory, HomePlace } from '@/types/place'

/** Demo destinations for Home UI (Phase 4). Marked as demo — not live inventory. */
export const HOME_CATEGORIES: HomeCategory[] = [
  { id: 'temples', label: 'Temples', slug: 'temple' },
  { id: 'beaches', label: 'Beaches', slug: 'beach' },
  { id: 'mountains', label: 'Mountains', slug: 'mountain' },
  { id: 'waterfalls', label: 'Waterfalls', slug: 'waterfall' },
  { id: 'historical', label: 'Historical', slug: 'historical' },
  { id: 'wildlife', label: 'Wildlife', slug: 'wildlife' },
  { id: 'adventure', label: 'Adventure', slug: 'adventure' },
  { id: 'food', label: 'Food', slug: 'food' },
  { id: 'hidden', label: 'Hidden gems', slug: 'hidden_gem' },
  { id: 'weekend', label: 'Weekend', slug: 'weekend' },
]

const COVER: Record<string, string> = {
  Temples: 'from-[#1b7a4e] to-[#0b3d91]',
  Beaches: 'from-[#0b3d91] to-[#1b7a4e]',
  Mountains: 'from-[#145c3b] to-[#5c6b63]',
  Waterfalls: 'from-[#0b3d91] to-[#5c6b63]',
  Historical: 'from-[#e07a2f] to-[#1b7a4e]',
  Wildlife: 'from-[#145c3b] to-[#e07a2f]',
  Nature: 'from-[#1b7a4e] to-[#145c3b]',
  City: 'from-[#0b3d91] to-[#14201a]',
  Food: 'from-[#e07a2f] to-[#0b3d91]',
}

const demo = (
  place: Omit<HomePlace, 'isDemo' | 'imageUrl'> & { imageUrl?: string },
): HomePlace => ({
  ...place,
  imageUrl: place.imageUrl ?? COVER[place.category] ?? 'from-[#1b7a4e] to-[#0b3d91]',
  isDemo: true,
})

export const HOME_PLACES: HomePlace[] = [
  demo({
    id: 'jaipur',
    name: 'Jaipur Pink City Circuit',
    location: 'Jaipur',
    state: 'Rajasthan',
    category: 'Historical',
    rating: 4.7,
    distanceKm: 5.2,
    estimatedCostInr: 2500,
    tags: ['popular', 'weekend', 'recommended', 'historical'],
  }),
  demo({
    id: 'goa',
    name: 'North Goa Beach Stretch',
    location: 'Panaji',
    state: 'Goa',
    category: 'Beaches',
    rating: 4.6,
    distanceKm: 12,
    estimatedCostInr: 3200,
    tags: ['popular', 'beach', 'weekend', 'recommended'],
  }),
  demo({
    id: 'manali',
    name: 'Solang Valley Meadows',
    location: 'Manali',
    state: 'Himachal Pradesh',
    category: 'Mountains',
    rating: 4.8,
    distanceKm: 14,
    estimatedCostInr: 4000,
    tags: ['popular', 'mountain', 'adventure', 'weekend'],
  }),
  demo({
    id: 'varanasi',
    name: 'Ghat Evening Trail',
    location: 'Varanasi',
    state: 'Uttar Pradesh',
    category: 'Temples',
    rating: 4.7,
    estimatedCostInr: 1800,
    tags: ['temple', 'popular', 'recommended'],
  }),
  demo({
    id: 'kochi',
    name: 'Fort Kochi Waterfront',
    location: 'Kochi',
    state: 'Kerala',
    category: 'City',
    rating: 4.5,
    distanceKm: 3.4,
    estimatedCostInr: 2200,
    tags: ['nearby', 'food', 'recommended', 'weekend'],
  }),
  demo({
    id: 'hampi',
    name: 'Hampi Ruins Circuit',
    location: 'Hampi',
    state: 'Karnataka',
    category: 'Historical',
    rating: 4.8,
    estimatedCostInr: 2100,
    tags: ['historical', 'hidden', 'budget', 'roadtrip'],
  }),
  demo({
    id: 'rishikesh',
    name: 'Rishikesh Riverside Trails',
    location: 'Rishikesh',
    state: 'Uttarakhand',
    category: 'Nature',
    rating: 4.6,
    estimatedCostInr: 2700,
    tags: ['nature', 'adventure', 'weekend', 'recommended'],
  }),
  demo({
    id: 'udaipur',
    name: 'Lake City Evening Walk',
    location: 'Udaipur',
    state: 'Rajasthan',
    category: 'City',
    rating: 4.7,
    estimatedCostInr: 3000,
    tags: ['popular', 'weekend', 'recommended'],
  }),
  demo({
    id: 'puri',
    name: 'Puri Seafront Promenade',
    location: 'Puri',
    state: 'Odisha',
    category: 'Beaches',
    rating: 4.4,
    estimatedCostInr: 1600,
    tags: ['beach', 'temple', 'budget'],
  }),
  demo({
    id: 'darjeeling',
    name: 'Tea Estate Viewpoints',
    location: 'Darjeeling',
    state: 'West Bengal',
    category: 'Mountains',
    rating: 4.6,
    estimatedCostInr: 2800,
    tags: ['mountain', 'hidden', 'weekend'],
  }),
  demo({
    id: 'vizag',
    name: 'RK Beach Promenade',
    location: 'Visakhapatnam',
    state: 'Andhra Pradesh',
    category: 'Beaches',
    rating: 4.5,
    distanceKm: 2.1,
    estimatedCostInr: 1200,
    tags: ['nearby', 'beach', 'weekend', 'budget'],
  }),
  demo({
    id: 'hyderabad',
    name: 'Old City Heritage Walk',
    location: 'Hyderabad',
    state: 'Telangana',
    category: 'Historical',
    rating: 4.5,
    distanceKm: 4.8,
    estimatedCostInr: 900,
    tags: ['nearby', 'historical', 'food', 'budget', 'trending'],
  }),
  demo({
    id: 'munnar',
    name: 'Tea Hills Day Escape',
    location: 'Munnar',
    state: 'Kerala',
    category: 'Nature',
    rating: 4.7,
    estimatedCostInr: 2600,
    tags: ['nature', 'mountain', 'weekend', 'roadtrip'],
  }),
  demo({
    id: 'athirappilly',
    name: 'Athirappilly Falls Lookout',
    location: 'Thrissur',
    state: 'Kerala',
    category: 'Waterfalls',
    rating: 4.6,
    estimatedCostInr: 1900,
    tags: ['waterfall', 'nature', 'weekend', 'roadtrip'],
  }),
  demo({
    id: 'bandipur',
    name: 'Bandipur Forest Edge',
    location: 'Bandipur',
    state: 'Karnataka',
    category: 'Wildlife',
    rating: 4.4,
    estimatedCostInr: 3500,
    tags: ['wildlife', 'adventure', 'weekend'],
  }),
  demo({
    id: 'pondicherry',
    name: 'Promenade & Cafe Lane',
    location: 'Puducherry',
    state: 'Puducherry',
    category: 'Food',
    rating: 4.5,
    estimatedCostInr: 2400,
    tags: ['food', 'weekend', 'roadtrip', 'trending'],
  }),
]

export function placesByTag(tag: string, limit = 8): HomePlace[] {
  return HOME_PLACES.filter((place) => place.tags.includes(tag)).slice(0, limit)
}

export function placesByCategory(category: string, limit = 8): HomePlace[] {
  const normalized = category.toLowerCase()
  return HOME_PLACES.filter(
    (place) =>
      place.category.toLowerCase() === normalized ||
      place.tags.includes(normalized.replace(/\s+/g, '_')) ||
      place.tags.includes(normalized),
  ).slice(0, limit)
}
