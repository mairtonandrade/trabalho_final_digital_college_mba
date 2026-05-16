"""Recria banco demo: cadastros + 6 meses + catálogo completo de fraudes."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.database import DB_PATH, init_db  # noqa: E402
from app.seed import seed_demo_data  # noqa: E402
from app.seed_cenarios_fraude import seed_catalogo_fraude  # noqa: E402
from app.seed_demo_historico import seed_historico_demo  # noqa: E402


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Removido: {DB_PATH}")
    init_db()
    seed_demo_data()
    seed_historico_demo(force=True)
    stats = seed_catalogo_fraude(force=True)
    print("Catálogo:", stats)


if __name__ == "__main__":
    main()
