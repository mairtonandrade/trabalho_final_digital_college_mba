#!/usr/bin/env python3
"""
Exporta snapshot JSON do seed do backend para o modo demo do frontend (Netlify).
Garante paridade: local (API) e deploy (VITE_DEMO_MODE) exibem os mesmos números.

Uso (na raiz do repo):
  python scripts/export_demo_snapshot.py

Saída: frontend/src/api/demoSnapshot.json
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

OUT_PATH = ROOT / "frontend" / "public" / "demoSnapshot.json"


def _json_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Não serializável: {type(obj)}")


def _model_list(items):
    return [i.model_dump(mode="json") for i in items]


def main() -> None:
    db_file = BACKEND / "guardiao_export.db"
    if db_file.exists():
        db_file.unlink()

    import os

    os.environ["DATABASE_URL"] = f"sqlite:///{db_file.as_posix()}"

    from app.database import SessionLocal, init_db
    from app.models import AuditLog, ContaBancaria, MovimentoConta, Remessa
    from app.routers.dashboard import (
        alertas_fraude,
        deteccoes_ia,
        kpis,
        pagamentos_nao_cadastrados,
        pagamentos_pf_nao_cadastrados,
        pontos_atencao,
    )
    from app.routers.remessas import _remessa_completa
    from app.seed import seed_demo_data
    from app.services.dashboard_historico import historico_controle_ia
    from app.services.dashboard_ia_metrics import metricas_ia_diretoria

    init_db()
    seed_demo_data()

    db = SessionLocal()
    try:
        remessas_all = db.query(Remessa).order_by(Remessa.created_at.desc()).all()
        remessas_out = [_remessa_completa(db, r, incluir_historico=True) for r in remessas_all]
        remessas_json = _model_list(remessas_out)

        historico = historico_controle_ia(db, limit=300)
        metricas = metricas_ia_diretoria(db, meses=6)

        contas = db.query(ContaBancaria).filter(ContaBancaria.ativa == 1).all()
        movimentos = (
            db.query(MovimentoConta).order_by(MovimentoConta.created_at.desc()).limit(80).all()
        )

        snapshot = {
            "meta": {
                "gerado_em": datetime.utcnow().isoformat() + "Z",
                "seed": "seed_demo_data + seed_catalogo_fraude",
                "kpis_diretoria_esperados": {
                    "pagamentos_analisados": len(historico["itens"]),
                    "execucoes_ia": sum(
                        len(i.get("analises_ia") or []) for i in historico["itens"]
                    ),
                    "fraudes_ml": historico["resumo"]["fraudes_ml"],
                },
            },
            "historicoControleIA": historico,
            "metricasIA": metricas,
            "kpis": kpis(db).model_dump(mode="json"),
            "auditoria": [
                {
                    "id": a.id,
                    "entity_type": a.entity_type,
                    "entity_id": a.entity_id,
                    "action": a.action,
                    "user_role": a.user_role,
                    "ip_address": a.ip_address or "127.0.0.1",
                    "details": a.details,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in db.query(AuditLog)
                .order_by(AuditLog.created_at.desc())
                .limit(200)
                .all()
            ],
            "deteccoesIA": deteccoes_ia(db),
            "alertas": alertas_fraude(db),
            "pagamentosNaoCadastrados": pagamentos_nao_cadastrados(db),
            "pagamentosPFNaoCadastrados": pagamentos_pf_nao_cadastrados(db),
            "pontosAtencao": _model_list(pontos_atencao(db)),
            "remessas": remessas_json,
            "contas": [
                {
                    "id": c.id,
                    "nome": c.nome,
                    "banco": c.banco,
                    "agencia": c.agencia,
                    "conta": c.conta,
                    "saldo": c.saldo,
                    "ativa": c.ativa,
                }
                for c in contas
            ],
            "movimentos": [
                {
                    "id": m.id,
                    "conta_id": m.conta_id,
                    "tipo": m.tipo,
                    "valor": m.valor,
                    "saldo_apos": m.saldo_apos,
                    "descricao": m.descricao,
                    "remessa_id": m.remessa_id,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in movimentos
            ],
        }

        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with OUT_PATH.open("w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2, default=_json_default)

        meta = snapshot["meta"]["kpis_diretoria_esperados"]
        print(f"OK -> {OUT_PATH}")
        print(
            f"  Pagamentos IA: {meta['pagamentos_analisados']} | "
            f"Execuções IA: {meta['execucoes_ia']} | "
            f"Fraudes ML: {meta['fraudes_ml']}"
        )
    finally:
        db.close()
        if db_file.exists():
            db_file.unlink()


if __name__ == "__main__":
    main()
