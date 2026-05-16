from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.limpar_dados import limpar_lancamentos

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/limpar-lancamentos")
def limpar(db: Session = Depends(get_db)):
    """Remove remessas e pagamentos (mantém fornecedores, colaboradores e contas)."""
    return limpar_lancamentos(db)
