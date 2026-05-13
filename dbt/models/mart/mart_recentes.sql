-- Mart: últimas 500 licitações — tabela detalhada no Power BI
SELECT
    numero_controle_pncp,
    orgao_nome,
    uf_sigla,
    municipio_nome,
    modalidade_nome,
    objeto_compra,
    valor_estimado,
    valor_homologado,
    situacao_nome,
    data_publicacao,
    data_encerramento,
    link_edital
FROM {{ ref('stg_licitacoes') }}
ORDER BY data_publicacao DESC
LIMIT 500
