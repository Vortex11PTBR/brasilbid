-- Mart: licitações por município — granularidade abaixo do UF
SELECT
    uf_sigla,
    municipio_nome,
    COUNT(*)                                            AS total_licitacoes,
    SUM(valor_estimado)                                 AS valor_total_estimado,
    COUNT(DISTINCT orgao_cnpj)                          AS total_orgaos,
    MAX(data_publicacao)                                AS ultima_publicacao
FROM {{ ref('stg_licitacoes') }}
WHERE municipio_nome IS NOT NULL
GROUP BY uf_sigla, municipio_nome
ORDER BY total_licitacoes DESC
