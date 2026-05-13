"""
Ponto de entrada: puxa dados do PNCP e faz upsert no PostgreSQL.

Uso:
    python run_ingestion.py                     # últimos 2 dias
    python run_ingestion.py --days 7            # últimos 7 dias
    python run_ingestion.py --date 2025-05-01   # data específica
"""
import argparse
import os
from datetime import date, timedelta

from ingestion.db import init_db
from ingestion.pncp import fetch_contratacoes, normalizar
from ingestion.upsert import upsert_batch

BATCH_SIZE = 200


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=int(os.getenv("PNCP_DAYS_BACK", "2")))
    parser.add_argument("--date", type=str, default=None, help="YYYY-MM-DD")
    args = parser.parse_args()

    if args.date:
        data_final = date.fromisoformat(args.date)
        data_inicial = data_final
    else:
        data_final = date.today()
        data_inicial = data_final - timedelta(days=args.days)

    print(f"🔄 Ingestão PNCP: {data_inicial} → {data_final}")
    init_db()

    batch: list[dict] = []
    total = 0

    for raw in fetch_contratacoes(data_inicial, data_final):
        row = normalizar(raw)
        if not row["numero_controle_pncp"]:
            continue
        batch.append(row)
        if len(batch) >= BATCH_SIZE:
            n = upsert_batch(batch)
            total += n
            print(f"  ↑ {total} registros inseridos/atualizados")
            batch.clear()

    if batch:
        total += upsert_batch(batch)

    print(f"✅ Concluído: {total} registros no banco")


if __name__ == "__main__":
    main()
