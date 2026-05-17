import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { ReactNode } from 'react'
import type { MetricasIAResponse } from '../api/client'

const CORES_TIPO: Record<string, string> = {
  fraude_ml: '#ef4444',
  pj_nao_cadastrado: '#f59e0b',
  pf_nao_cadastrado: '#a855f7',
  risco_alto: '#f97316',
  risco_medio: '#eab308',
  conformidade: '#10b981',
}

const CORES_PERFIL: Record<string, string> = {
  analista: '#22d3ee',
  gerente: '#a78bfa',
  sistema: '#fbbf24',
  diretoria: '#34d399',
}

const LABELS_PERFIL: Record<string, string> = {
  analista: 'Analista',
  gerente: 'Gerente',
  sistema: 'Sistema / IA',
  diretoria: 'Diretoria',
}

const DESCRICOES_PERFIL: Record<string, (qtd: number) => string> = {
  analista: (n) =>
    `Analista: ${n} execuções da IA ao enviar ou reenviar remessas ao gerente.`,
  gerente: (n) =>
    `Gerente: ${n} reanálises da IA (botão "Nova análise IA" ou remessa devolvida corrigida).`,
  sistema: (n) =>
    `Sistema / IA: ${n} execuções automáticas (pipeline, catálogo ou reprocessamento).`,
}

function rotuloPerfil(perfil: string, label?: string): string {
  return LABELS_PERFIL[perfil] || label || perfil.charAt(0).toUpperCase() + perfil.slice(1)
}

const tooltipStyle = {
  background: '#1e293b',
  border: '1px solid #94a3b8',
  borderRadius: 8,
  fontSize: 13,
  color: '#f8fafc',
}

function ChartShell({
  title,
  subtitle,
  help,
  borderClass,
  children,
}: {
  title: string
  subtitle: string
  help?: ReactNode
  borderClass: string
  children: ReactNode
}) {
  return (
    <div
      className={`flex flex-col rounded-xl border p-4 sm:p-5 min-h-[380px] ${borderClass} bg-gradient-to-br from-slate-950/80 to-slate-900/40`}
    >
      <header className="mb-3 shrink-0">
        <h3 className="text-sm font-semibold text-slate-100">{title}</h3>
        <p className="text-xs text-slate-300 mt-0.5">{subtitle}</p>
        {help && (
          <div className="mt-2 border-l-2 border-cyan-600/50 pl-3">{help}</div>
        )}
      </header>
      <div className="flex-1 min-h-[240px] w-full min-w-0">{children}</div>
    </div>
  )
}

export default function PainelGraficosIA({ data }: { data: MetricasIAResponse | null }) {
  if (!data) {
    return (
      <section className="mb-8 rounded-xl border border-slate-800 bg-slate-900/40 p-5">
        <p className="text-slate-500 text-sm">Carregando gráficos de detecção IA...</p>
      </section>
    )
  }

  const dadosPerfil = data.por_perfil.map((p) => ({
    ...p,
    label: rotuloPerfil(p.perfil, p.label),
  }))
  const totalPerfil = dadosPerfil.reduce((s, p) => s + p.quantidade, 0)

  return (
    <section className="mb-8">
      <div className="mb-5">
        <h2 className="font-semibold text-lg text-slate-100">Painéis de detecção IA</h2>
        <p className="text-sm text-slate-300 mt-1 max-w-4xl">
          Indicadores e gráficos usam o mesmo período dos filtros. O total de execuções IA
          coincide com a soma do gráfico por perfil (quem disparou cada análise).
        </p>
        {data.resumo && (
          <div className="flex flex-wrap gap-2 mt-3 text-xs">
            <span className="px-2 py-1 rounded border border-slate-600 text-slate-200">
              {totalPerfil || data.resumo.total_analises} execuções IA
            </span>
            <span className="px-2 py-1 rounded border border-slate-600 text-slate-300">
              {data.resumo.total_pagamentos_ia} pagamentos analisados
            </span>
            <span className="px-2 py-1 rounded border border-red-800 text-red-300">
              {data.resumo.fraudes_ml} fraudes ML
            </span>
          </div>
        )}
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <ChartShell
          title="Quem disparou a análise IA"
          subtitle="Execuções por perfil responsável pelo gatilho"
          help={
            dadosPerfil.length > 0 ? (
              <ul className="space-y-1.5 text-xs text-slate-200">
                {dadosPerfil.map((p) => (
                  <li key={p.perfil}>
                    {DESCRICOES_PERFIL[p.perfil]?.(p.quantidade) ??
                      `${p.label}: ${p.quantidade} execuções no período.`}
                  </li>
                ))}
              </ul>
            ) : undefined
          }
          borderClass="border-cyan-800/40"
        >
          <ResponsiveContainer width="100%" height={260}>
            <BarChart
              layout="vertical"
              data={dadosPerfil}
              margin={{ top: 4, right: 24, left: 4, bottom: 4 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
              <XAxis type="number" stroke="#cbd5e1" fontSize={11} allowDecimals={false} />
              <YAxis
                type="category"
                dataKey="label"
                stroke="#cbd5e1"
                fontSize={12}
                width={108}
                tickLine={false}
              />
              <Tooltip
                contentStyle={tooltipStyle}
                formatter={(value) => [`${Number(value ?? 0)} execuções`, 'IA']}
                labelFormatter={(label) => `Perfil: ${label}`}
              />
              <Bar dataKey="quantidade" name="Execuções IA" radius={[0, 4, 4, 0]} barSize={32}>
                {dadosPerfil.map((item) => (
                  <Cell key={item.perfil} fill={CORES_PERFIL[item.perfil] || '#64748b'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          {totalPerfil > 0 && (
            <ul className="mt-3 space-y-1.5 text-xs text-slate-300 border-t border-slate-700 pt-3">
              {dadosPerfil.map((p) => (
                <li key={p.perfil} className="flex justify-between gap-2">
                  <span className="font-medium">{p.label}</span>
                  <span className="text-slate-100 tabular-nums">
                    {p.quantidade} ({Math.round((p.quantidade / totalPerfil) * 100)}%)
                  </span>
                </li>
              ))}
            </ul>
          )}
        </ChartShell>

        <ChartShell
          title="Evolução mensal"
          subtitle="Quantidade de execuções IA por mês"
          help={`Cada ponto soma execuções IA no mês. Total no período: ${data.resumo.total_analises} (= badge e gráfico por perfil).`}
          borderClass="border-violet-800/40"
        >
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={data.por_mes} margin={{ top: 12, right: 16, left: 0, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis
                dataKey="label"
                stroke="#94a3b8"
                fontSize={11}
                interval={0}
                angle={data.por_mes.length > 4 ? -25 : 0}
                textAnchor={data.por_mes.length > 4 ? 'end' : 'middle'}
                height={data.por_mes.length > 4 ? 48 : 30}
              />
              <YAxis stroke="#94a3b8" fontSize={11} allowDecimals={false} width={36} />
              <Tooltip
                contentStyle={tooltipStyle}
                formatter={(value) => [`${Number(value ?? 0)} execuções`, 'IA no mês']}
              />
              <Line
                type="monotone"
                dataKey="quantidade"
                name="Execuções"
                stroke="#a78bfa"
                strokeWidth={2.5}
                dot={{ fill: '#a78bfa', strokeWidth: 2, r: 5 }}
                activeDot={{ r: 7 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartShell>

        <ChartShell
          title="Tipo de detecção"
          subtitle="Classificação do resultado por pagamento (última análise)"
          help={`Cada pagamento entra em uma categoria prioritária. Total: ${data.resumo.total_pagamentos_ia} pagamentos (= indicador "Pagamentos analisados"). Fraudes ML: ${data.resumo.fraudes_ml}.`}
          borderClass="border-amber-800/40"
        >
          <div className="flex flex-col sm:flex-row gap-4 h-full min-h-[240px]">
            <div className="sm:w-[55%] min-h-[200px]">
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={data.por_tipo_deteccao}
                    dataKey="quantidade"
                    nameKey="label"
                    cx="50%"
                    cy="50%"
                    innerRadius={42}
                    outerRadius={78}
                    paddingAngle={2}
                    label={false}
                  >
                    {data.por_tipo_deteccao.map((item) => (
                      <Cell key={item.tipo} fill={CORES_TIPO[item.tipo] || '#64748b'} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={tooltipStyle} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <ul className="sm:w-[45%] flex flex-col justify-center gap-2 text-xs">
              {data.por_tipo_deteccao.map((item) => {
                const total = data.por_tipo_deteccao.reduce((s, t) => s + t.quantidade, 0)
                const pct = total ? Math.round((item.quantidade / total) * 100) : 0
                return (
                  <li key={item.tipo} className="flex items-center gap-2">
                    <span
                      className="w-2.5 h-2.5 rounded-full shrink-0"
                      style={{ background: CORES_TIPO[item.tipo] || '#64748b' }}
                    />
                    <span className="text-slate-300 flex-1">{item.label}</span>
                    <span className="text-slate-400 tabular-nums shrink-0">
                      {item.quantidade} ({pct}%)
                    </span>
                  </li>
                )
              })}
            </ul>
          </div>
        </ChartShell>
      </div>
    </section>
  )
}
