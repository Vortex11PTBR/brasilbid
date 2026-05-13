-- Staging: limpa e tipifica os dados brutos
SELECT
    numero_controle_pncp,
    orgao_cnpj,
    TRIM(orgao_nome)                                    AS orgao_nome,
    modalidade_id,
    TRIM(modalidade_nome)                               AS modalidade_nome,
    TRIM(modo_disputa_nome)                             AS modo_disputa_nome,
    TRIM(objeto_compra)                                 AS objeto_compra,
    COALESCE(valor_total_estimado, 0)                   AS valor_estimado,
    COALESCE(valor_homologado, 0)                       AS valor_homologado,
    UPPER(TRIM(uf_sigla))                               AS uf_sigla,
    TRIM(municipio_nome)                                AS municipio_nome,
    TRIM(situacao_nome)                                 AS situacao_nome,
    data_publicacao::DATE                               AS data_publicacao,
    data_encerramento::DATE                             AS data_encerramento,
    link_edital,
    numero_compra,
    ano_compra,
    ingested_at
FROM {{ source('public', 'licitacoes') }}
WHERE numero_controle_pncp IS NOT NULL
