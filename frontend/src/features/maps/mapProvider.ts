/** Map provider abstraction — Leaflet/OSM now; Google/Mapbox later. */

export type MapLatLng = {
  lat: number
  lng: number
}

export type MapBounds = {
  north: number
  south: number
  east: number
  west: number
}

export type MapMarkerModel = {
  id: string
  position: MapLatLng
  title: string
  subtitle?: string
  href?: string
  tone?: 'green' | 'saffron' | 'blue'
}

export type MapProviderId = 'leaflet_osm'

export const DEFAULT_MAP_PROVIDER: MapProviderId = 'leaflet_osm'

export const INDIA_CENTER: MapLatLng = { lat: 22.5, lng: 79.0 }
export const INDIA_DEFAULT_ZOOM = 5

export const DEMO_CITY_PRESETS: Array<{
  id: string
  label: string
  center: MapLatLng
  zoom: number
}> = [
  { id: 'india', label: 'All India', center: INDIA_CENTER, zoom: 5 },
  { id: 'hyderabad', label: 'Hyderabad', center: { lat: 17.385, lng: 78.486 }, zoom: 11 },
  { id: 'goa', label: 'Goa', center: { lat: 15.49, lng: 73.82 }, zoom: 10 },
  { id: 'jaipur', label: 'Jaipur', center: { lat: 26.91, lng: 75.79 }, zoom: 11 },
  { id: 'manali', label: 'Manali', center: { lat: 32.24, lng: 77.19 }, zoom: 11 },
]

export function boundsFromLeaflet(b: {
  getNorth: () => number
  getSouth: () => number
  getEast: () => number
  getWest: () => number
}): MapBounds {
  return {
    north: b.getNorth(),
    south: b.getSouth(),
    east: b.getEast(),
    west: b.getWest(),
  }
}
