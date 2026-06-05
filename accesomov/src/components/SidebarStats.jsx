const NIVEL_COLORS = {
  '2-Buena':    '#22c55e',
  '3-Media':    '#eab308',
  '4-Mala':     '#f97316',
  '5-Muy mala': '#ef4444',
}

function Skeleton({ className = '' }) {
  return <div className={`bg-gray-800 rounded animate-pulse ${className}`} />
}

function StatCard({ value, label, color = 'text-white' }) {
  return (
    <div className="bg-gray-800 rounded-lg p-3">
      <div className={`text-2xl font-bold ${color}`}>{value}</div>
      <div className="text-xs text-gray-400 mt-0.5">{label}</div>
    </div>
  )
}

export default function SidebarStats({ resumen, loading }) {
  if (loading) {
    return (
      <div className="p-4 space-y-3 flex-shrink-0">
        <Skeleton className="h-4 w-36" />
        <div className="grid grid-cols-2 gap-2">
          <Skeleton className="h-16" />
          <Skeleton className="h-16" />
        </div>
        <Skeleton className="h-28" />
        <Skeleton className="h-16" />
      </div>
    )
  }

  if (!resumen) return null

  const {
    total_colonias,
    score_promedio,
    distribucion_nivel_score,
    colonias_alto_riesgo,
    peor_colonia,
  } = resumen

  return (
    <div className="p-4 space-y-3 flex-shrink-0">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
        Resumen · Tlalpan
      </p>

      <div className="grid grid-cols-2 gap-2">
        <StatCard value={total_colonias} label="Colonias" />
        <StatCard
          value={score_promedio}
          label="Score promedio"
          color="text-orange-400"
        />
      </div>

      <div className="grid grid-cols-2 gap-2">
        <StatCard
          value={colonias_alto_riesgo}
          label="En riesgo (≥4)"
          color="text-red-400"
        />
        <StatCard
          value={`${Math.round((colonias_alto_riesgo / total_colonias) * 100)}%`}
          label="Del total"
          color="text-red-300"
        />
      </div>

      {/* Distribución por nivel */}
      <div className="bg-gray-800 rounded-lg p-3 space-y-2">
        <p className="text-xs text-gray-400 font-medium">Distribución</p>
        {Object.entries(distribucion_nivel_score).map(([nivel, count]) => {
          const color = NIVEL_COLORS[nivel] ?? '#6b7280'
          const pct = Math.round((count / total_colonias) * 100)
          const label = nivel.split('-')[1]
          return (
            <div key={nivel}>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-300">{label}</span>
                <span className="text-gray-500">
                  {count} · {pct}%
                </span>
              </div>
              <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all"
                  style={{ width: `${pct}%`, backgroundColor: color }}
                />
              </div>
            </div>
          )
        })}
      </div>

      {/* Peor colonia */}
      <div className="bg-red-950/40 border border-red-900/50 rounded-lg p-3">
        <p className="text-xs text-red-400 font-semibold mb-1">⚠ Peor accesibilidad</p>
        <p className="text-sm text-white font-medium leading-snug">
          {peor_colonia.colonia}
        </p>
        <p className="text-xs text-gray-400 mt-1">
          Score {peor_colonia.score_accesibilidad}/5 · {peor_colonia.INFRAPEAT}
        </p>
      </div>
    </div>
  )
}
