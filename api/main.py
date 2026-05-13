"""
BrasilBid FastAPI — REST API sobre os marts dbt
Documentação: http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import municipios, oportunidades, stats

app = FastAPI(
    title="BrasilBid API",
    description="REST API sobre dados de licitações públicas brasileiras (PNCP)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(oportunidades.router, prefix="/oportunidades", tags=["Oportunidades"])
app.include_router(municipios.router, prefix="/municipios", tags=["Municípios"])
app.include_router(stats.router, prefix="/stats", tags=["Estatísticas"])


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "brasilbid-api"}
