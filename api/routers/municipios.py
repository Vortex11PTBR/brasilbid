import pandas as pd
from fastapi import APIRouter, Query
from sqlalchemy import text

from api.database import get_engine

router = APIRouter()


@router.get("/", summary="Licitações agrupadas por município")
def list_municipios(
    uf: str | None = Query(None, description="Filtrar por UF (ex: SP)"),
    limit: int = Query(100, ge=1, le=500),
):
    q = "SELECT * FROM public_mart.mart_por_municipio"
    params = {"limit": limit}
    if uf:
        q += " WHERE uf = :uf"
        params["uf"] = uf.upper()
    q += " ORDER BY total_licitacoes DESC LIMIT :limit"

    with get_engine().connect() as conn:
        df = pd.read_sql(text(q), conn, params=params)
    return df.to_dict(orient="records")
