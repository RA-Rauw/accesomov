import { forwardRef, useImperativeHandle, useRef, useCallback, useState } from 'react'
import Map, { Source, Layer } from 'react-map-gl'

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN

const INITIAL_VIEW = { longitude: -99.1332, latitude: 19.2954, zoom: 12 }

// score ≤2.5 → verde | ≤3.5 → amarillo | ≤4.5 → naranja | >4.5 → rojo
const COLOR_EXPR = [
  'case',
  ['<=', ['get', 'score_accesibilidad'], 2.5], '#22c55e',
  ['<=', ['get', 'score_accesibilidad'], 3.5], '#eab308',
  ['<=', ['get', 'score_accesibilidad'], 4.5], '#f97316',
  '#ef4444',
]

const MapView = forwardRef(function MapView(
  { geojson, selectedCveCol, onColoniaClick },
  ref
) {
  const mapRef = useRef(null)
  const [cursor, setCursor] = useState('auto')

  useImperativeHandle(ref, () => ({
    flyTo: (lng, lat) => {
      mapRef.current?.flyTo({ center: [lng, lat], zoom: 15, duration: 1500 })
    },
  }), [])

  const handleClick = useCallback(
    (event) => {
      const feature = event.features?.[0]
      if (feature) onColoniaClick(feature.properties.cve_col)
    },
    [onColoniaClick]
  )

  const handleMouseMove = useCallback((event) => {
    setCursor(event.features?.length > 0 ? 'pointer' : 'auto')
  }, [])

  const handleMouseLeave = useCallback(() => setCursor('auto'), [])

  return (
    // flex-1 toma el espacio disponible; position:relative ancla los hijos absolutos
    <div className="flex-1 relative">
      {/*
        El div absolutamente posicionado le da al Map dimensiones de píxeles
        reales, evitando que height:100% falle al resolver a través de flex.
      */}
      <div style={{ position: 'absolute', inset: 0 }}>
        <Map
          ref={mapRef}
          mapboxAccessToken={MAPBOX_TOKEN}
          initialViewState={INITIAL_VIEW}
          mapStyle="mapbox://styles/mapbox/dark-v11"
          interactiveLayerIds={geojson ? ['colonias-fill'] : []}
          onClick={handleClick}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          cursor={cursor}
          style={{ width: '100%', height: '100%' }}
        >
          {geojson && (
            <Source id="colonias" type="geojson" data={geojson}>
              {/* Relleno coloreado por score */}
              <Layer
                id="colonias-fill"
                type="fill"
                paint={{
                  'fill-color': COLOR_EXPR,
                  'fill-opacity': 0.7,
                }}
              />
              {/* Borde fino general */}
              <Layer
                id="colonias-outline"
                type="line"
                paint={{
                  'line-color': 'rgba(255,255,255,0.12)',
                  'line-width': 0.5,
                }}
              />
              {/* Borde blanco grueso de la colonia seleccionada */}
              <Layer
                id="colonias-selected"
                type="line"
                paint={{
                  'line-color': '#ffffff',
                  'line-width': 2.5,
                }}
                filter={['==', ['get', 'cve_col'], selectedCveCol ?? '']}
              />
            </Source>
          )}
        </Map>

        {/* Overlay de carga mientras llega el GeoJSON */}
        {!geojson && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="bg-gray-900/90 rounded-xl px-5 py-3 flex items-center gap-3 text-sm text-gray-300 shadow-xl">
              <svg className="animate-spin h-4 w-4 text-blue-400" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Cargando colonias…
            </div>
          </div>
        )}

        {/* Hint de interacción */}
        {geojson && !selectedCveCol && (
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 pointer-events-none">
            <div className="bg-gray-900/80 backdrop-blur-sm text-gray-400 text-xs px-3 py-1.5 rounded-full border border-gray-700">
              Haz click en una colonia para ver su detalle
            </div>
          </div>
        )}
      </div>
    </div>
  )
})

export default MapView
