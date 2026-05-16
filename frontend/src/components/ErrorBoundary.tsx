import { Component, type ErrorInfo, type ReactNode } from 'react'

export default class ErrorBoundary extends Component<
  { children: ReactNode },
  { error: Error | null }
> {
  state = { error: null as Error | null }

  static getDerivedStateFromError(error: Error) {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('ErrorBoundary', error, info)
  }

  render() {
    if (this.state.error) {
      return (
        <div className="min-h-screen flex items-center justify-center p-6 bg-slate-950">
          <div className="glass-panel max-w-lg p-8 text-center">
            <p className="text-red-400 font-semibold mb-2">Erro na interface</p>
            <p className="text-slate-400 text-sm mb-4">{this.state.error.message}</p>
            <button
              type="button"
              className="btn-primary"
              onClick={() => {
                window.location.href = '/'
              }}
            >
              Voltar ao início
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
