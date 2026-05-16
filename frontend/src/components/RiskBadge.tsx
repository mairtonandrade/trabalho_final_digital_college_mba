export default function RiskBadge({ level, score }: { level: string; score?: number }) {
  const styles: Record<string, string> = {
    baixo: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
    medio: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
    alto: 'bg-red-500/20 text-red-300 border-red-500/40',
  }
  return (
    <span
      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium border ${
        styles[level] || styles.baixo
      }`}
    >
      {level.toUpperCase()}
      {score !== undefined && ` ${(score * 100).toFixed(0)}%`}
    </span>
  )
}
