-- Mart: licitações por UF — usado no mapa do Power BI
SELECT
    uf_sigla,
    COUNT(*)                                            AS total_licitacoes,
    SUM(valor_estimado)                                 AS valor_total_estimado,
    SUM(valor_homologado)                               AS valor_total_homologado,
    AVG(valor_estimado)                                 AS valor_medio_estimado,
    COUNT(DISTINCT orgao_cnpj)                          AS total_orgaos
FROM {{ ref('stg_licitacoes') }}
WHERE uf_sigla IS NOT NULL
GROUP BY uf_sigla
ORDER BY total_licitacoes DESC
