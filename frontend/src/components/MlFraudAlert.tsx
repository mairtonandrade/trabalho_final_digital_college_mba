export default function MlFraudAlert({
  detectada,
  score,
  motivos,
}: {
  detectada?: number | boolean
  score?: number
  motivos?: string | null
}) {
  if (!detectada && (score ?? 0) < 0.55) return null
  const lista = motivos?.split('; ').filter(Boolean) ?? []
  return (
    <div className="mt-2 p-3 rounded-lg bg-red-950/40 border border-red-700/60 text-xs">
      <p className="font-semibold text-red-300 mb-1">
        Modelo ML: {detectada ? 'FRAUDE DETECTADA' : 'Risco elevado'} ({((score ?? 0) * 100).toFixed(0)}%)
      </p>
      <ul className="list-disc list-inside text-slate-300 space-y-0.5">
        {lista.slice(0, 4).map((m, i) => (
          <li key={i}>{m}</li>
        ))}
      </ul>
    </div>
  )
}
