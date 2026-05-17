import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { MetricasIAResponse } from '../api/client'

const CORES_TIPO = ['#ef4444', '#f59e0b', '#a855f7', '#f97316', '#eab308', '#10b981']
const CORES_PERFIL = ['#22d3ee', '#a78bfa', '#fbbf24']

const tooltipStyle = { background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }

export default function PainelGraficosIA({ data }: { data: MetricasIAResponse | null }) {
  if (!data) {
    return (
      <section className="mb-8 rounded-xl border border-slate-800 bg-slate-900/40 p-5">
        <p className="text-slate-500 text-sm">Carregando gráficos de detecção IA...</p>
      </section>
    )
  }

  return (
    <section className="mb-8">
      <div className="mb-4">
        <h2 className="font-semibold text-lg text-slate-100">Painéis de detecção IA</h2>
        <p className="text-sm text-slate-400 mt-1">
          Acompanhamento por perfil que disparou a análise, evolução mensal e distribuição por tipo de
          detecção.
          {data.resumo && (
            <span className="text-slate-500 ml-1">
              ({data.resumo.total_analises} análises · {data.resumo.fraudes_ml} fraudes ML)
            </span>
          )}
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="p-5 rounded-xl border border-cyan-800/40 bg-gradient-to-br from-cyan-950/20 to-slate-950 h-80">
          <h3 className="text-sm font-semibold text-cyan-300 mb-1">Por perfil (gatilho da análise)</h3>
          <p className="text-xs text-slate-500 mb-3">Analista, Gerente ou Sistema ao executar a IA</p>
          <ResponsiveContainer width="100%" height="78%">
            <BarChart data={data.por_perfil} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="label" stroke="#94a3b8" fontSize={11} />
              <YAxis stroke="#94a3b8" allowDecimals={false} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="quantidade" name="Análises" radius={[4, 4, 0, 0]}>
                {data.por_perfil.map((_, i) => (
                  <Cell key={i} fill={CORES_PERFIL[i % CORES_PERFIL.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="p-5 rounded-xl border border-violet-800/40 bg-gradient-to-br from-violet-950/20 to-slate-950 h-80">
          <h3 className="text-sm font-semibold text-violet-300 mb-1">Por mês</h3>
          <p className="text-xs text-slate-500 mb-3">Volume de análises IA nos últimos meses</p>
          <ResponsiveContainer width="100%" height="78%">
            <LineChart data={data.por_mes} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="label" stroke="#94a3b8" fontSize={11} />
              <YAxis stroke="#94a3b8" allowDecimals={false} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line
                type="monotone"
                dataKey="quantidade"
                name="Análises"
                stroke="#a78bfa"
                strokeWidth={2}
                dot={{ fill: '#a78bfa', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="p-5 rounded-xl border border-amber-800/40 bg-gradient-to-br from-amber-950/20 to-slate-950 h-80">
          <h3 className="text-sm font-semibold text-amber-300 mb-1">Por tipo de detecção</h3>
          <p className="text-xs text-slate-500 mb-3">Fraude ML, cadastro, risco e conformidade</p>
          <ResponsiveContainer width="100%" height="78%">
            <PieChart>
              <Pie
                data={data.por_tipo_deteccao}
                dataKey="quantidade"
                nameKey="label"
                cx="50%"
                cy="50%"
                outerRadius={72}
                label={(props) => {
                  const nome = String(props.name ?? '')
                  const qtd = Number(props.value ?? 0)
                  return qtd > 0 ? `${nome}: ${qtd}` : ''
                }}
                labelLine={false}
              >
                {data.por_tipo_deteccao.map((_, i) => (
                  <Cell key={i} fill={CORES_TIPO[i % CORES_TIPO.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  )
}
