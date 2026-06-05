import { useState } from 'react'

function scoreColor(score) {
  if (score >= 5) return '#ef4444'
  if (score >= 4.5) return '#f97316'
  return '#fb923c'
}

function Skeleton() {
  return (
    <div className="px-4 py-2 space-y-2">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="h-8 bg-gray-800 rounded animate-pulse" />
      ))}
    </div>
  )
}

export default function ZonasRiesgo({ colonias, loading, onSelect }) {
  const [open, setOpen] = useState(true)

  return (
    <div className="flex flex-col flex-1 min-h-0 border-t border-gray-800">
      {/* Header colapsable */}
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex-shrink-0 flex items-center justify-between px-4 py-3 hover:bg-gray-800/60 transition-colors text-left"
      >
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-300">Zonas de riesgo</span>
          <span className="bg-red-900/70 text-red-300 text-xs font-semibold px-1.5 py-0.5 rounded">
            {loading ? '…' : colonias.length}
          </span>
        </div>
        <span className="text-gray-500 text-[10px]">{open ? '▲' : '▼'}</span>
      </button>

      {/* Lista */}
      {open && (
        <div className="flex-1 overflow-y-auto sidebar-scroll min-h-0">
          {loading ? (
            <Skeleton />
          ) : (
            <ul>
              {colonias.map((col) => (
                <li key={col.cve_col}>
                  <button
                    onClick={() => onSelect(col.centroide.lng, col.centroide.lat)}
                    className="w-full flex items-center gap-3 px-4 py-2 hover:bg-gray-800/70 transition-colors text-left group"
                  >
                    {/* Indicador de color */}
                    <span
                      className="flex-shrink-0 w-1.5 h-6 rounded-full"
                      style={{ backgroundColor: scoreColor(col.score_accesibilidad) }}
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-gray-300 truncate group-hover:text-white leading-tight">
                        {col.colonia}
                      </p>
                      <p className="text-[10px] text-gray-500 mt-0.5">{col.INFRAPEAT}</p>
                    </div>
                    <span
                      className="flex-shrink-0 text-xs font-bold tabular-nums"
                      style={{ color: scoreColor(col.score_accesibilidad) }}
                    >
                      {col.score_accesibilidad}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
