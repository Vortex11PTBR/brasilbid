import pandas as pd
from fastapi import APIRouter, Query
from sqlalchemy import text

from api.database import get_engine

router = APIRouter()


@router.get("/resumo", summary="Estatísticas gerais do banco de dados")
def resumo():
    queries = {
        "total_licitacoes": "SELECT COUNT(*) AS n FROM raw.contratacoes",
        "oportunidades_ativas": "SELECT COUNT(*) AS n FROM public_mart.mart_oportunidades",
        "estados_cobertos": "SELECT COUNT(DISTINCT uf) AS n FROM public_mart.mart_por_uf",
    }
    result = {}
    with get_engine().connect() as conn:
        for key, q in queries.items():
            row = conn.execute(text(q)).fetchone()
            result[key] = row[0] if row else 0
    return result


@router.get("/por-uf", summary="Licitações por estado (UF)")
def por_uf():
    with get_engine().connect() as conn:
        df = pd.read_sql(
            "SELECT * FROM public_mart.mart_por_uf ORDER BY total_licitacoes DESC",
            conn,
        )
    return df.to_dict(orient="records")


@router.get("/ranking-orgaos", summary="Ranking de órgãos contratantes")
def ranking_orgaos(limit: int = Query(20, ge=1, le=100)):
    with get_engine().connect() as conn:
        df = pd.read_sql(
            text(
                "SELECT * FROM public_mart.mart_ranking_orgaos "
                "ORDER BY total_licitacoes DESC LIMIT :limit"
            ),
            conn,
            params={"limit": limit},
        )
    return df.to_dict(orient="records")
