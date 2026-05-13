-- Mart: série temporal diária — gráfico de linha no Power BI
SELECT
    data_publicacao,
    modalidade_nome,
    COUNT(*)                                            AS total_licitacoes,
    SUM(valor_estimado)                                 AS valor_total_estimado
FROM {{ ref('stg_licitacoes') }}
WHERE data_publicacao IS NOT NULL
GROUP BY data_publicacao, modalidade_nome
ORDER BY data_publicacao DESC
