#!/usr/bin/env python3
"""Valida que demoSnapshot.json bate com o seed fresco do backend."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "frontend" / "public" / "demoSnapshot.json"


def main() -> int:
    if not SNAPSHOT.exists():
        print(f"ERRO: snapshot ausente. Rode: python scripts/export_demo_snapshot.py")
        return 1

    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    itens = snap["historicoControleIA"]["itens"]
    pag = len(itens)
    exec_ia = sum(len(i.get("analises_ia") or []) for i in itens)
    fraudes = sum(1 for i in itens if i.get("ml_fraude_detectada"))

    esperado = snap["meta"]["kpis_diretoria_esperados"]
    ok = (
        pag == esperado["pagamentos_analisados"]
        and exec_ia == esperado["execucoes_ia"]
        and fraudes == esperado["fraudes_ml"]
    )

    print(f"Snapshot: pagamentos={pag} execucoes={exec_ia} fraudes={fraudes}")
    if ok:
        print("OK: KPIs internos consistentes.")
        return 0
    print(f"ERRO: esperado {esperado}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
