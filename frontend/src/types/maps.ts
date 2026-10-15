export type MapPin = {
  id: string
  name: string
  slug: string
  entity_type: string
  latitude: number
  longitude: number
  city_name: string
  state_code: string
  category_slug: string | null
  rating_avg: number
  is_seed_data: boolean
  href: string
}

export type CityMapCenter = {
  id: string
  name: string
  slug: string
  state_code: string
  latitude: number
  longitude: number
  place_count: number
  is_seed_data: boolean
}

export type MapPinsData = {
  pins: MapPin[]
  total: number
  provider: string
  notice: string
}
