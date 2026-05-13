-- Mart: distribuição por modalidade de licitação
SELECT
    modalidade_nome,
    modo_disputa_nome,
    COUNT(*)                                            AS total_licitacoes,
    SUM(valor_estimado)                                 AS valor_total_estimado,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER ()
    , 2)                                                AS pct_total
FROM {{ ref('stg_licitacoes') }}
WHERE modalidade_nome IS NOT NULL
GROUP BY modalidade_nome, modo_disputa_nome
ORDER BY total_licitacoes DESC
