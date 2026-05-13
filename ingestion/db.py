"""Conexão e schema PostgreSQL (Neon)."""
import os
from sqlalchemy import (
    create_engine, text, Column, Text, Integer, Numeric,
    TIMESTAMP, Index
)
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


class Base(DeclarativeBase):
    pass


DDL = """
CREATE TABLE IF NOT EXISTS licitacoes (
    numero_controle_pncp TEXT PRIMARY KEY,
    orgao_cnpj           TEXT,
    orgao_nome           TEXT,
    modalidade_id        INTEGER,
    modalidade_nome      TEXT,
    modo_disputa_nome    TEXT,
    objeto_compra        TEXT,
    valor_total_estimado NUMERIC,
    valor_homologado     NUMERIC,
    uf_sigla             TEXT,
    municipio_nome       TEXT,
    situacao_nome        TEXT,
    data_publicacao      TIMESTAMPTZ,
    data_encerramento    TIMESTAMPTZ,
    data_inclusao        TIMESTAMPTZ,
    link_edital          TEXT,
    numero_compra        TEXT,
    ano_compra           INTEGER,
    ingested_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lic_uf         ON licitacoes(uf_sigla);
CREATE INDEX IF NOT EXISTS idx_lic_modalidade  ON licitacoes(modalidade_id);
CREATE INDEX IF NOT EXISTS idx_lic_data        ON licitacoes(data_publicacao DESC);
CREATE INDEX IF NOT EXISTS idx_lic_situacao    ON licitacoes(situacao_nome);
"""


def init_db() -> None:
    with engine.connect() as conn:
        conn.execute(text(DDL))
        conn.commit()
    print("✅ Schema OK")
