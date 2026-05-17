# -*- coding: utf-8 -*-
"""Gera PNGs em docs/assets a partir dos SVGs (UTF-8 com entidades XML)."""
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "docs" / "assets"

# SVGs adicionais (02-05) com texto legível
EXTRA = {
    "02-analista.svg": """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675" fill="none">
  <rect width="1200" height="675" fill="#0b0f1a"/>
  <rect x="0" y="0" width="1200" height="64" fill="#020617"/>
  <text x="40" y="40" fill="#34d399" font-family="Segoe UI,Arial,sans-serif" font-size="14" font-weight="600">ANALISTA</text>
  <text x="40" y="100" fill="#f1f5f9" font-family="Segoe UI,Arial,sans-serif" font-size="22" font-weight="700">Remessas e pagamentos</text>
  <text x="40" y="130" fill="#cbd5e1" font-family="Segoe UI,Arial,sans-serif" font-size="13">O que deseja fazer?</text>
  <rect x="40" y="150" width="260" height="90" rx="12" fill="#064e3b" stroke="#10b981" stroke-width="2"/>
  <rect x="320" y="150" width="260" height="90" rx="12" fill="#0f172a" stroke="#475569"/>
  <rect x="600" y="150" width="260" height="90" rx="12" fill="#0f172a" stroke="#475569"/>
  <rect x="880" y="150" width="260" height="90" rx="12" fill="#0f172a" stroke="#475569"/>
  <text x="170" y="190" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">Remessas</text>
  <text x="450" y="190" text-anchor="middle" fill="#e2e8f0" font-size="13" font-weight="600">Novos cadastros</text>
  <text x="730" y="190" text-anchor="middle" fill="#e2e8f0" font-size="13" font-weight="600">Consultar cadastros</text>
  <text x="1010" y="190" text-anchor="middle" fill="#e2e8f0" font-size="13" font-weight="600">Contas e extrato</text>
  <rect x="40" y="270" width="1120" height="360" rx="16" fill="#0f172a" stroke="#475569"/>
  <text x="60" y="310" fill="#fff" font-size="16" font-weight="600">Remessa de pagamentos</text>
  <rect x="60" y="330" width="180" height="36" rx="8" fill="#059669"/>
  <text x="150" y="353" text-anchor="middle" fill="#fff" font-size="12">Nova remessa</text>
  <rect x="60" y="390" width="1060" height="48" rx="8" fill="#1e293b" stroke="#64748b"/>
  <text x="80" y="420" fill="#e2e8f0" font-size="13">Remessa #26 &#183; Conta operacional &#183; 3 pagamentos</text>
  <rect x="60" y="460" width="1060" height="140" rx="8" fill="#1e293b" stroke="#64748b"/>
  <text x="80" y="495" fill="#cbd5e1" font-size="12">Pagamento PJ &#183; R$ 45.200,00</text>
  <text x="80" y="525" fill="#cbd5e1" font-size="12">Pagamento PF sal&#225;rio &#183; R$ 8.500,00</text>
  <rect x="60" y="620" width="1060" height="40" rx="8" fill="#7c3aed"/>
  <text x="590" y="645" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">Enviar remessa ao gerente (an&#225;lise IA)</text>
</svg>""",
    "03-gerente-ia.svg": """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675" fill="none">
  <rect width="1200" height="675" fill="#0b0f1a"/>
  <text x="40" y="40" fill="#a78bfa" font-family="Segoe UI,Arial,sans-serif" font-size="14" font-weight="600">GERENTE</text>
  <text x="40" y="100" fill="#fff" font-size="22" font-weight="700">Aprova&#231;&#245;es e revis&#227;o IA</text>
  <rect x="40" y="130" width="270" height="80" rx="12" fill="#064e3b" stroke="#10b981" stroke-width="2"/>
  <rect x="330" y="130" width="270" height="80" rx="12" fill="#0f172a" stroke="#475569"/>
  <rect x="620" y="130" width="270" height="80" rx="12" fill="#0f172a" stroke="#475569"/>
  <rect x="910" y="130" width="250" height="80" rx="12" fill="#0f172a" stroke="#475569"/>
  <text x="175" y="175" text-anchor="middle" fill="#fff" font-size="12" font-weight="600">Remessas</text>
  <text x="465" y="175" text-anchor="middle" fill="#e2e8f0" font-size="12" font-weight="600">Fornecedores</text>
  <rect x="40" y="240" width="1120" height="380" rx="16" fill="#0f172a" stroke="#7c3aed"/>
  <text x="60" y="280" fill="#fff" font-size="16" font-weight="600">Remessa #12 &#183; aguardando 2&#170; assinatura</text>
  <text x="60" y="310" fill="#f87171" font-size="12">Modelo ML detectou fraude &#8212; justificativa obrigat&#243;ria</text>
  <rect x="60" y="330" width="1080" height="100" rx="8" fill="#1e293b"/>
  <text x="80" y="365" fill="#e2e8f0" font-size="12">PAY-000042 &#183; Fornecedor XYZ &#183; R$ 28.400,00 &#183; Score alto</text>
  <text x="80" y="395" fill="#94a3b8" font-size="11">Parecer GenAI: diverg&#234;ncia documental identificada...</text>
  <rect x="60" y="450" width="140" height="36" rx="8" fill="#059669"/>
  <text x="130" y="473" text-anchor="middle" fill="#fff" font-size="11">Liberar</text>
  <rect x="220" y="450" width="140" height="36" rx="8" fill="#dc2626"/>
  <text x="290" y="473" text-anchor="middle" fill="#fff" font-size="11">Devolver</text>
</svg>""",
    "04-diretoria.svg": """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675" fill="none">
  <rect width="1200" height="675" fill="#0b0f1a"/>
  <text x="40" y="40" fill="#34d399" font-size="14" font-weight="600">DIRETORIA</text>
  <text x="40" y="95" fill="#fff" font-size="22" font-weight="700">Vis&#227;o executiva</text>
  <rect x="40" y="115" width="200" height="70" rx="10" fill="#064e3b" stroke="#10b981" stroke-width="2"/>
  <rect x="260" y="115" width="200" height="70" rx="10" fill="#0f172a" stroke="#475569"/>
  <rect x="480" y="115" width="200" height="70" rx="10" fill="#0f172a" stroke="#475569"/>
  <text x="140" y="155" text-anchor="middle" fill="#fff" font-size="11" font-weight="600">Dashboard</text>
  <rect x="40" y="210" width="170" height="72" rx="10" fill="#1e293b" stroke="#475569"/>
  <rect x="230" y="210" width="170" height="72" rx="10" fill="#1e293b" stroke="#475569"/>
  <rect x="420" y="210" width="170" height="72" rx="10" fill="#1e293b" stroke="#475569"/>
  <rect x="610" y="210" width="170" height="72" rx="10" fill="#7f1d1d" stroke="#ef4444"/>
  <text x="125" y="245" text-anchor="middle" fill="#94a3b8" font-size="10">SALDO TOTAL</text>
  <text x="125" y="268" text-anchor="middle" fill="#fff" font-size="14" font-weight="700">R$ 1.535.000</text>
  <text x="695" y="245" text-anchor="middle" fill="#fca5a5" font-size="10">FRAUDES IA</text>
  <text x="695" y="268" text-anchor="middle" fill="#fecaca" font-size="14" font-weight="700">28</text>
  <rect x="40" y="300" width="560" height="320" rx="12" fill="#0f172a" stroke="#06b6d4"/>
  <rect x="620" y="300" width="540" height="320" rx="12" fill="#0f172a" stroke="#a78bfa"/>
  <text x="60" y="335" fill="#e2e8f0" font-size="13" font-weight="600">Execu&#231;&#245;es IA por perfil</text>
  <text x="640" y="335" fill="#e2e8f0" font-size="13" font-weight="600">Evolu&#231;&#227;o mensal</text>
  <rect x="80" y="380" width="320" height="24" rx="4" fill="#22d3ee"/>
  <text x="420" y="397" fill="#cbd5e1" font-size="12">Analista: 74 execu&#231;&#245;es</text>
</svg>""",
    "05-fluxo-ia.svg": """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 400" fill="none">
  <rect width="1200" height="400" fill="#0b0f1a"/>
  <text x="600" y="45" text-anchor="middle" fill="#fff" font-size="20" font-weight="700">Fluxo de an&#225;lise IA</text>
  <rect x="60" y="80" width="200" height="80" rx="12" fill="#1e293b" stroke="#22d3ee"/>
  <text x="160" y="125" text-anchor="middle" fill="#e2e8f0" font-size="12">Analista monta remessa</text>
  <path d="M270 120 H330" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>
  <rect x="340" y="80" width="200" height="80" rx="12" fill="#1e293b" stroke="#a78bfa"/>
  <text x="440" y="118" text-anchor="middle" fill="#e2e8f0" font-size="12">Envio dispara</text>
  <text x="440" y="138" text-anchor="middle" fill="#c4b5fd" font-size="12">XGBoost + GenAI</text>
  <path d="M550 120 H610" stroke="#64748b" stroke-width="2"/>
  <rect x="620" y="80" width="200" height="80" rx="12" fill="#1e293b" stroke="#f59e0b"/>
  <text x="720" y="125" text-anchor="middle" fill="#e2e8f0" font-size="12">Gerente revisa</text>
  <path d="M830 120 H890" stroke="#64748b" stroke-width="2"/>
  <rect x="900" y="80" width="200" height="80" rx="12" fill="#1e293b" stroke="#10b981"/>
  <text x="1000" y="125" text-anchor="middle" fill="#e2e8f0" font-size="12">Libera&#231;&#227;o / auditoria</text>
  <rect x="200" y="220" width="800" height="120" rx="12" fill="#0f172a" stroke="#475569"/>
  <text x="600" y="260" text-anchor="middle" fill="#94a3b8" font-size="13">Hist&#243;rico versionado em PagamentoAnaliseIA + trilha WORM</text>
  <text x="600" y="290" text-anchor="middle" fill="#f87171" font-size="12">Fraude ML e n&#227;o cadastrados geram alertas na Diretoria</text>
  <defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#64748b"/></marker></defs>
</svg>""",
}

for name, content in EXTRA.items():
    (ASSETS / name).write_text(content, encoding="utf-8")

try:
    import resvg_py

    for svg in ASSETS.glob("*.svg"):
        png = svg.with_suffix(".png")
        resvg_py.svg_to_png(svg.read_text(encoding="utf-8"), write_to=str(png), width=1200)
        print("ok", png.name)
except ImportError:
    try:
        import subprocess
        import sys

        for svg in sorted(ASSETS.glob("*.svg")):
            png = svg.with_suffix(".png")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "resvg-py", "-q"],
                check=False,
                capture_output=True,
            )
            import resvg_py

            resvg_py.svg_to_png(svg.read_text(encoding="utf-8"), write_to=str(png), width=1200)
            print("ok", png.name)
            break
    except Exception as e:
        print("PNG skip (install resvg-py):", e)
        print("SVGs atualizados com UTF-8; PNG manual ou: pip install resvg-py")
