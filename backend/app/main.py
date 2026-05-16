from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import admin, cadastros, colaboradores, contas, dashboard, fornecedores, ml, pagamentos, remessas
from app.seed import seed_demo_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_demo_data()
    yield


app = FastAPI(
    title="Pagamentos Anti-Fraude API",
    description="MBA Digital College - Aprovação dupla + IA",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router, prefix="/api")
app.include_router(contas.router, prefix="/api")
app.include_router(cadastros.router, prefix="/api")
app.include_router(colaboradores.router, prefix="/api")
app.include_router(fornecedores.router, prefix="/api")
app.include_router(remessas.router, prefix="/api")
app.include_router(pagamentos.router, prefix="/api")
app.include_router(ml.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "pagamentos-anti-fraude"}
