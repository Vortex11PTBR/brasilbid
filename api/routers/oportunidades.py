import pandas as pd
from fastapi import APIRouter, Query
from sqlalchemy import text

from api.database import get_engine

router = APIRouter()


@router.get("/", summary="Lista oportunidades ativas de licitação")
def list_oportunidades(
    uf: str | None = Query(None, description="Filtrar por UF (ex: SP)"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros"),
):
    q = "SELECT * FROM public_mart.mart_oportunidades"
    params = {}
    if uf:
        q += " WHERE uf = :uf"
        params["uf"] = uf.upper()
    q += " LIMIT :limit"
    params["limit"] = limit

    with get_engine().connect() as conn:
        df = pd.read_sql(text(q), conn, params=params)
    return df.to_dict(orient="records")
