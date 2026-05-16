import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "pagamentos.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _add_column_if_missing(conn, table: str, column: str, col_def: str):
    rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
    names = {r[1] for r in rows}
    if column not in names:
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}"))
        conn.commit()


def run_migrations():
    with engine.connect() as conn:
        _add_column_if_missing(conn, "remessas", "conta_bancaria_id", "INTEGER")
        _add_column_if_missing(conn, "remessas", "valor_total", "REAL DEFAULT 0")
        _add_column_if_missing(
            conn, "pagamentos", "fornecedor_nao_cadastrado", "INTEGER DEFAULT 0"
        )
        for col, typedef in [
            ("tipo_beneficiario", "TEXT DEFAULT 'pj'"),
            ("colaborador_id", "INTEGER"),
            ("beneficiario_nome", "TEXT"),
            ("beneficiario_documento", "TEXT"),
            ("tipo_despesa", "TEXT DEFAULT 'fornecedor'"),
            ("competencia", "TEXT"),
            ("pf_nao_cadastrado", "INTEGER DEFAULT 0"),
            ("ml_fraude_detectada", "INTEGER DEFAULT 0"),
            ("ml_motivos", "TEXT"),
        ]:
            _add_column_if_missing(conn, "pagamentos", col, typedef)
        for col, typedef in [
            ("revisado_gerente", "INTEGER DEFAULT 0"),
            ("revisado_documentos", "INTEGER DEFAULT 0"),
            ("revisado_valores", "INTEGER DEFAULT 0"),
            ("revisado_em", "TEXT"),
            ("revisado_observacao", "TEXT"),
            ("ponto_atencao_diretoria", "INTEGER DEFAULT 0"),
            ("ia_analisado", "INTEGER DEFAULT 0"),
        ]:
            _add_column_if_missing(conn, "pagamentos", col, typedef)
        _add_column_if_missing(conn, "remessas", "motivo_devolucao", "TEXT")
        _add_column_if_missing(conn, "remessas", "analise_ia_concluida", "INTEGER DEFAULT 0")
        _add_column_if_missing(conn, "colaboradores", "updated_at", "TEXT")
        _add_column_if_missing(conn, "fornecedores", "updated_at", "TEXT")
        conn.execute(
            text("UPDATE colaboradores SET status = 'ativo' WHERE status = 'aprovado'")
        )
        conn.execute(
            text("UPDATE fornecedores SET status = 'ativo' WHERE status = 'aprovado'")
        )
        conn.commit()


def init_db():
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    run_migrations()
