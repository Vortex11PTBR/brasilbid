-- Mart: top órgãos por volume de licitações e valor
SELECT
    orgao_cnpj,
    orgao_nome,
    uf_sigla,
    COUNT(*)                                            AS total_licitacoes,
    SUM(valor_estimado)                                 AS valor_total_estimado,
    SUM(valor_homologado)                               AS valor_total_homologado,
    MAX(data_publicacao)                                AS ultima_publicacao
FROM {{ ref('stg_licitacoes') }}
WHERE orgao_nome IS NOT NULL
GROUP BY orgao_cnpj, orgao_nome, uf_sigla
ORDER BY total_licitacoes DESC
