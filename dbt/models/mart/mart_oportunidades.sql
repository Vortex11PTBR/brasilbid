-- Mart: licitações abertas — oportunidades ativas para fornecedores
-- Atualizado diariamente; encerramento >= hoje e sem status final
{{
    config(materialized='table')
}}
SELECT
    numero_controle_pncp,
    orgao_nome,
    uf_sigla,
    municipio_nome,
    modalidade_nome,
    objeto_compra,
    valor_estimado,
    link_edital,
    data_publicacao,
    data_encerramento,
    (data_encerramento - CURRENT_DATE)              AS dias_restantes
FROM {{ ref('stg_licitacoes') }}
WHERE
    data_encerramento >= CURRENT_DATE
    AND situacao_nome NOT ILIKE '%cancelad%'
    AND situacao_nome NOT ILIKE '%homologad%'
    AND situacao_nome NOT ILIKE '%encerrad%'
    AND situacao_nome NOT ILIKE '%revogad%'
ORDER BY data_encerramento ASC
