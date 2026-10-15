import { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { MapLatLng, MapMarkerModel } from '@/features/maps/mapProvider'
import { cn } from '@/utils/cn'

export type MapCanvasProps = {
  center: MapLatLng
  zoom?: number
  markers?: MapMarkerModel[]
  route?: MapLatLng[]
  className?: string
  fitMarkers?: boolean
  onBoundsChange?: (bounds: {
    north: number
    south: number
    east: number
    west: number
  }) => void
  onMarkerSelect?: (marker: MapMarkerModel) => void
}

const TONE_CLASS: Record<NonNullable<MapMarkerModel['tone']>, string> = {
  green: '#1b7a4e',
  saffron: '#e07a2f',
  blue: '#0b3d91',
}

function makeIcon(tone: MapMarkerModel['tone'] = 'green') {
  const color = TONE_CLASS[tone]
  return L.divIcon({
    className: 'by-map-marker',
    html: `<span style="
      display:block;width:16px;height:16px;border-radius:9999px;
      background:${color};border:2px solid #fff;
      box-shadow:0 2px 6px rgba(20,32,26,.35);
    "></span>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  })
}

export function MapCanvas({
  center,
  zoom = 12,
  markers = [],
  route,
  className,
  fitMarkers = false,
  onBoundsChange,
  onMarkerSelect,
}: MapCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<L.Map | null>(null)
  const layerRef = useRef<L.LayerGroup | null>(null)
  const onBoundsChangeRef = useRef(onBoundsChange)
  const onMarkerSelectRef = useRef(onMarkerSelect)
  const initialViewRef = useRef({ center, zoom })

  useEffect(() => {
    onBoundsChangeRef.current = onBoundsChange
  }, [onBoundsChange])

  useEffect(() => {
    onMarkerSelectRef.current = onMarkerSelect
  }, [onMarkerSelect])

  useEffect(() => {
    const el = containerRef.current
    if (!el || mapRef.current) return

    const { center: start, zoom: startZoom } = initialViewRef.current
    const map = L.map(el, {
      zoomControl: true,
      attributionControl: true,
    }).setView([start.lat, start.lng], startZoom)

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(map)

    layerRef.current = L.layerGroup().addTo(map)

    const emitBounds = () => {
      const b = map.getBounds()
      onBoundsChangeRef.current?.({
        north: b.getNorth(),
        south: b.getSouth(),
        east: b.getEast(),
        west: b.getWest(),
      })
    }

    map.whenReady(() => {
      map.invalidateSize()
      emitBounds()
    })
    map.on('moveend', emitBounds)

    mapRef.current = map
    return () => {
      map.off('moveend', emitBounds)
      map.remove()
      mapRef.current = null
      layerRef.current = null
    }
  }, [])

  useEffect(() => {
    const map = mapRef.current
    if (!map) return
    map.setView([center.lat, center.lng], zoom, { animate: true })
    window.setTimeout(() => map.invalidateSize(), 50)
  }, [center.lat, center.lng, zoom])

  useEffect(() => {
    const map = mapRef.current
    const layer = layerRef.current
    if (!map || !layer) return

    layer.clearLayers()
    const latLngs: L.LatLngExpression[] = []

    for (const marker of markers) {
      const leafletMarker = L.marker([marker.position.lat, marker.position.lng], {
        icon: makeIcon(marker.tone),
        title: marker.title,
      })
      const html = `
        <strong>${escapeHtml(marker.title)}</strong>
        ${marker.subtitle ? `<br/><span>${escapeHtml(marker.subtitle)}</span>` : ''}
      `
      leafletMarker.bindPopup(html)
      leafletMarker.on('click', () => onMarkerSelectRef.current?.(marker))
      leafletMarker.addTo(layer)
      latLngs.push([marker.position.lat, marker.position.lng])
    }

    if (route && route.length >= 2) {
      const line = L.polyline(
        route.map((point) => [point.lat, point.lng] as L.LatLngExpression),
        { color: '#0b3d91', weight: 3, opacity: 0.75, dashArray: '6 8' },
      )
      line.addTo(layer)
      for (const point of route) {
        latLngs.push([point.lat, point.lng])
      }
    }

    if (fitMarkers && latLngs.length > 0) {
      map.fitBounds(L.latLngBounds(latLngs), { padding: [36, 36], maxZoom: 13 })
    }
  }, [markers, route, fitMarkers])

  return (
    <div
      ref={containerRef}
      className={cn(
        'h-72 w-full overflow-hidden rounded-[1.25rem] border border-by-border bg-by-green-soft',
        className,
      )}
      role="application"
      aria-label="Interactive map"
    />
  )
}

function escapeHtml(value: string) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
}
