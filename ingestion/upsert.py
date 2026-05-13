"""Upsert em batch no PostgreSQL."""
from sqlalchemy import text
from .db import engine

UPSERT_SQL = text("""
INSERT INTO licitacoes (
    numero_controle_pncp, orgao_cnpj, orgao_nome,
    modalidade_id, modalidade_nome, modo_disputa_nome,
    objeto_compra, valor_total_estimado, valor_homologado,
    uf_sigla, municipio_nome, situacao_nome,
    data_publicacao, data_encerramento, data_inclusao,
    link_edital, numero_compra, ano_compra
) VALUES (
    :numero_controle_pncp, :orgao_cnpj, :orgao_nome,
    :modalidade_id, :modalidade_nome, :modo_disputa_nome,
    :objeto_compra, :valor_total_estimado, :valor_homologado,
    :uf_sigla, :municipio_nome, :situacao_nome,
    :data_publicacao, :data_encerramento, :data_inclusao,
    :link_edital, :numero_compra, :ano_compra
)
ON CONFLICT (numero_controle_pncp) DO UPDATE SET
    situacao_nome        = EXCLUDED.situacao_nome,
    valor_homologado     = EXCLUDED.valor_homologado,
    valor_total_estimado = EXCLUDED.valor_total_estimado,
    data_encerramento    = EXCLUDED.data_encerramento,
    ingested_at          = NOW()
""")


def upsert_batch(records: list[dict]) -> int:
    if not records:
        return 0
    with engine.begin() as conn:
        conn.execute(UPSERT_SQL, records)
    return len(records)
