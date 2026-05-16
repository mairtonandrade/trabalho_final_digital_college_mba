"""Remove remessas, pagamentos e análises — mantém cadastros base."""

from pathlib import Path

from sqlalchemy.orm import Session

from app.models import AuditLog, MovimentoConta, Pagamento, PagamentoAnaliseIA, PagamentoAnexo, Remessa

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"


def limpar_lancamentos(db: Session) -> dict:
    for anexo in db.query(PagamentoAnexo).all():
        try:
            Path(anexo.caminho).unlink(missing_ok=True)
        except OSError:
            pass
    for p in db.query(Pagamento).all():
        if p.documento_path:
            try:
                Path(p.documento_path).unlink(missing_ok=True)
            except OSError:
                pass

    n_analises = db.query(PagamentoAnaliseIA).delete()
    n_anexos = db.query(PagamentoAnexo).delete()
    n_pag = db.query(Pagamento).delete()
    n_mov = db.query(MovimentoConta).filter(MovimentoConta.remessa_id.isnot(None)).delete()
    n_rem = db.query(Remessa).delete()
    db.query(AuditLog).filter(AuditLog.entity_type.in_(["remessa", "pagamento"])).delete()
    db.commit()

    return {
        "remessas": n_rem,
        "pagamentos": n_pag,
        "anexos": n_anexos,
        "analises_ia": n_analises,
        "movimentos_remessa": n_mov,
    }
