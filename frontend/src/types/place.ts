export type HomePlace = {
  id: string
  name: string
  location: string
  state: string
  category: string
  rating: number
  distanceKm?: number
  estimatedCostInr: number
  imageUrl: string
  tags: string[]
  isDemo: true
}

export type HomeCategory = {
  id: string
  label: string
  slug: string
}
