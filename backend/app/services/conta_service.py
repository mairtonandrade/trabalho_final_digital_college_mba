from sqlalchemy.orm import Session

from app.models import ContaBancaria, MovimentoConta, Pagamento, Remessa
from app.services.audit_service import registrar


def creditar_receita(
    db: Session, conta_id: int, valor: float, descricao: str, user_role: str = "analista"
) -> ContaBancaria:
    conta = db.query(ContaBancaria).filter(ContaBancaria.id == conta_id).first()
    if not conta:
        raise ValueError("Conta não encontrada")
    if valor <= 0:
        raise ValueError("Valor deve ser positivo")
    conta.saldo += valor
    mov = MovimentoConta(
        conta_id=conta.id,
        tipo="receita",
        valor=valor,
        saldo_apos=conta.saldo,
        descricao=descricao or "Receita creditada",
    )
    db.add(mov)
    db.commit()
    db.refresh(conta)
    registrar(
        db,
        "conta_bancaria",
        conta.id,
        "receita_creditada",
        user_role,
        {"valor": valor, "saldo_apos": conta.saldo},
    )
    return conta


def debitar_remessa(
    db: Session, conta_id: int, remessa: Remessa, pagamentos: list[Pagamento]
) -> ContaBancaria:
    conta = db.query(ContaBancaria).filter(ContaBancaria.id == conta_id).first()
    if not conta:
        raise ValueError("Conta não encontrada")
    total = sum(p.valor for p in pagamentos)
    if conta.saldo < total:
        raise ValueError(
            f"Saldo insuficiente. Disponível: R$ {conta.saldo:,.2f}, necessário: R$ {total:,.2f}"
        )
    conta.saldo -= total
    mov = MovimentoConta(
        conta_id=conta.id,
        tipo="debito_remessa",
        valor=total,
        saldo_apos=conta.saldo,
        descricao=f"Débito remessa #{remessa.id} — {remessa.titulo}",
        remessa_id=remessa.id,
    )
    db.add(mov)
    remessa.valor_total = total
    db.commit()
    db.refresh(conta)
    registrar(
        db,
        "conta_bancaria",
        conta.id,
        "debito_remessa",
        "sistema",
        {"remessa_id": remessa.id, "valor": total, "saldo_apos": conta.saldo},
    )
    return conta


def verificar_saldo_remessa(db: Session, remessa: Remessa, pagamentos: list[Pagamento]) -> tuple[bool, str, float]:
    if not remessa.conta_bancaria_id:
        return False, "Selecione a conta bancária de origem da remessa.", 0.0
    conta = db.query(ContaBancaria).filter(ContaBancaria.id == remessa.conta_bancaria_id).first()
    if not conta:
        return False, "Conta bancária não encontrada.", 0.0
    total = sum(p.valor for p in pagamentos)
    if conta.saldo < total:
        return (
            False,
            f"Saldo insuficiente na conta {conta.nome}. Disponível: R$ {conta.saldo:,.2f}, remessa: R$ {total:,.2f}",
            total,
        )
    return True, "", total
