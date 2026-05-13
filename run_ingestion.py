"""
Ponto de entrada: puxa dados do PNCP e faz upsert no PostgreSQL.

Uso:
    python run_ingestion.py                     # últimos 2 dias
    python run_ingestion.py --days 7            # últimos 7 dias
    python run_ingestion.py --date 2026-05-01   # data específica
"""
import argparse
import logging
import os
import sys
from datetime import date, timedelta

from ingestion.db import init_db
from ingestion.pncp import fetch_contratacoes, normalizar
from ingestion.upsert import upsert_batch

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

BATCH_SIZE = 200


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingestão PNCP → PostgreSQL")
    parser.add_argument("--days", type=int, default=int(os.getenv("PNCP_DAYS_BACK", "2")),
                        help="Número de dias para ingerir (padrão: 2)")
    parser.add_argument("--date", type=str, default=None, metavar="YYYY-MM-DD",
                        help="Data específica para ingerir")
    args = parser.parse_args()

    if args.date:
        data_final = date.fromisoformat(args.date)
        data_inicial = data_final
    else:
        data_final = date.today()
        data_inicial = data_final - timedelta(days=args.days)

    log.info("Iniciando ingestão PNCP: %s → %s", data_inicial, data_final)
    init_db()

    batch: list[dict] = []
    total = 0
    skipped = 0

    for raw in fetch_contratacoes(data_inicial, data_final):
        row = normalizar(raw)
        if not row["numero_controle_pncp"]:
            skipped += 1
            continue
        batch.append(row)
        if len(batch) >= BATCH_SIZE:
            n = upsert_batch(batch)
            total += n
            log.info("Upsert parcial: %d registros acumulados", total)
            batch.clear()

    if batch:
        total += upsert_batch(batch)

    log.info("─" * 50)
    log.info("✅ Ingestão concluída")
    log.info("   Registros inseridos/atualizados : %d", total)
    log.info("   Registros ignorados (sem PK)    : %d", skipped)
    log.info("   Período                         : %s → %s", data_inicial, data_final)

    if total == 0:
        log.warning("Nenhum registro ingerido — verifique a API do PNCP ou o período informado")
        sys.exit(1)


if __name__ == "__main__":
    main()
