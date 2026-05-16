from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import Pagamento
from app.services.utils import benford_suspeito


def velocity_rule(db: Session, fornecedor_id: int, valor: float) -> tuple[bool, str]:
    """Mesmo fornecedor com 3+ pagamentos no dia ou fracionamento."""
    hoje = datetime.utcnow().date()
    pagamentos = (
        db.query(Pagamento)
        .filter(Pagamento.fornecedor_id == fornecedor_id)
        .all()
    )
    hoje_count = sum(1 for p in pagamentos if p.created_at.date() == hoje)
    hoje_total = sum(p.valor for p in pagamentos if p.created_at.date() == hoje)

    flags = []
    if hoje_count >= 2:
        flags.append(f"Velocity: {hoje_count + 1}º pagamento ao mesmo fornecedor hoje")
    if hoje_total + valor > 100000 and valor < 50000:
        flags.append("Possível fracionamento para burlar alçada (>100k fracionado)")

    suspeito = len(flags) > 0
    return suspeito, "; ".join(flags) if flags else ""


def regras_heuristicas(
    db: Session, fornecedor_id: int, valor: float, razao_social: str, cnpj: str
) -> tuple[float, list[str]]:
    flags = []
    score = 0.0

    if benford_suspeito(valor):
        flags.append("Valor com padrão atípico (Benford/heurística)")
        score += 0.15

    vel, vel_msg = velocity_rule(db, fornecedor_id, valor)
    if vel:
        flags.append(vel_msg)
        score += 0.25

    if valor > 200000:
        flags.append("Valor acima do limite operacional padrão (R$ 200.000)")
        score += 0.2

    if len(razao_social.strip()) < 5:
        flags.append("Razão social incompleta")
        score += 0.1

    return min(score, 0.5), flags
