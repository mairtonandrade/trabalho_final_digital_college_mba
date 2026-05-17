export interface ModuloItem {
  id: string
  titulo: string
  descricao: string
  icone: string
}

export default function ModuloSelector({
  modulos,
  ativo,
  onChange,
}: {
  modulos: ModuloItem[]
  ativo: string
  onChange: (id: string) => void
}) {
  return (
    <div className="mb-8">
      <p className="text-sm font-medium text-slate-200 mb-3">O que deseja fazer?</p>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {modulos.map((m) => {
          const selected = ativo === m.id
          return (
            <button
              key={m.id}
              type="button"
              onClick={() => onChange(m.id)}
              className={`module-card text-left ${selected ? 'module-card--active' : ''}`}
            >
              <span className="text-2xl mb-2 block" aria-hidden>
                {m.icone}
              </span>
              <h3 className="text-sm font-semibold text-white leading-snug">{m.titulo}</h3>
              <p className="text-xs text-slate-300 mt-1 leading-relaxed">{m.descricao}</p>
            </button>
          )
        })}
      </div>
    </div>
  )
}

