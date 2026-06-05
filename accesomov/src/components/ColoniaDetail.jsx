const INFRAPEAT_STYLE = {
  Alta:  { dot: '#22c55e', badge: 'bg-green-900/40 text-green-300 border-green-800/60' },
  Media: { dot: '#eab308', badge: 'bg-yellow-900/40 text-yellow-300 border-yellow-800/60' },
  Baja:  { dot: '#f97316', badge: 'bg-orange-900/40 text-orange-300 border-orange-800/60' },
  Nula:  { dot: '#ef4444', badge: 'bg-red-900/40 text-red-300 border-red-800/60' },
}

function scoreColor(score) {
  if (score <= 2.5) return '#22c55e'
  if (score <= 3.5) return '#eab308'
  if (score <= 4.5) return '#f97316'
  return '#ef4444'
}

function Skeleton() {
  return (
    <div className="space-y-3">
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 bg-gray-800 rounded-full animate-pulse flex-shrink-0" />
        <div className="flex-1 space-y-2">
          <div className="h-5 bg-gray-800 rounded animate-pulse w-56" />
          <div className="flex gap-2">
            <div className="h-4 bg-gray-800 rounded animate-pulse w-20" />
            <div className="h-4 bg-gray-800 rounded animate-pulse w-24" />
          </div>
        </div>
      </div>
      <div className="space-y-1.5">
        <div className="h-3.5 bg-gray-800 rounded animate-pulse" />
        <div className="h-3.5 bg-gray-800 rounded animate-pulse w-5/6" />
        <div className="h-3.5 bg-gray-800 rounded animate-pulse w-4/6" />
      </div>
    </div>
  )
}

export default function ColoniaDetail({ data, loading, onClose }) {
  const infra = data ? (INFRAPEAT_STYLE[data.INFRAPEAT] ?? INFRAPEAT_STYLE.Nula) : null
  const color = data ? scoreColor(data.score_accesibilidad) : null

  return (
    <div className="flex-shrink-0 bg-gray-900/95 backdrop-blur-sm border-t border-gray-700/80 px-5 py-4">
      <div className="flex items-start gap-4">
        {/* Icono accesibilidad */}
        <div className="flex-shrink-0 w-9 h-9 rounded-full bg-gray-800 flex items-center justify-center text-lg mt-0.5">
          ♿
        </div>

        {/* Contenido */}
        <div className="flex-1 min-w-0">
          {loading ? (
            <Skeleton />
          ) : data ? (
            <>
              {/* Header */}
              <div className="flex items-baseline gap-3 flex-wrap mb-2">
                <h3 className="text-sm font-bold text-white leading-tight">
                  {data.colonia}
                </h3>
                <div className="flex items-center gap-2 flex-wrap">
                  {/* Score */}
                  <span
                    className="text-sm font-bold tabular-nums"
                    style={{ color }}
                  >
                    {data.score_accesibilidad}/5
                  </span>
                  <span className="text-gray-600">·</span>
                  {/* INFRAPEAT badge */}
                  <span
                    className={`text-xs px-2 py-0.5 rounded border font-medium ${infra.badge}`}
                  >
                    Peatonal: {data.INFRAPEAT}
                  </span>
                  {/* Nivel */}
                  <span className="text-xs text-gray-500">{data.nivel_acceso}</span>
                  {/* Población */}
                  {data.pob_2010 && (
                    <span className="text-xs text-gray-600">
                      · {data.pob_2010.toLocaleString('es-MX')} hab.
                    </span>
                  )}
                </div>
              </div>

              {/* Descripción IA */}
              <p className="text-sm text-gray-300 leading-relaxed">
                {data.descripcion_ia}
              </p>
            </>
          ) : null}
        </div>

        {/* Botón cerrar */}
        <button
          onClick={onClose}
          className="flex-shrink-0 w-7 h-7 flex items-center justify-center rounded-full text-gray-500 hover:text-white hover:bg-gray-700 transition-colors text-sm mt-0.5"
          aria-label="Cerrar"
        >
          ✕
        </button>
      </div>
    </div>
  )
}
