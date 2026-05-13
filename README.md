# 🏛️ BrasilBid — Monitor de Licitações Públicas

> Pipeline ETL que ingere licitações do PNCP via API oficial, transforma com dbt, expõe via FastAPI e serve dashboard ao vivo com Streamlit e Power BI. Transparência pública em dados reais.

[![Pipeline Status](https://github.com/Vortex11PTBR/brasilibid/actions/workflows/ingest.yml/badge.svg)](https://github.com/Vortex11PTBR/brasilibid/actions/workflows/ingest.yml)
[![Live App](https://img.shields.io/badge/Streamlit-Live%20Dashboard-FF4B4B?logo=streamlit)](https://brasilbid.streamlit.app)
[![Power BI](https://img.shields.io/badge/Power%20BI-Live%20Dashboard-yellow?logo=powerbi)](https://app.powerbi.com/view?r=eyJrIjoiYjQzNDdiMmMtMzczMi00MmY0LWIyZjMtMDg2NTEwNTUzZjE2IiwidCI6ImY5OTZjZmRiLTQyYWMtNGVhZC1iYzQzLThmZmY3Njc0Zjg4NiIsImMiOjR9&pageName=c90308a9d2662513e95b)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![dbt](https://img.shields.io/badge/dbt-1.10-orange?logo=dbt)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)
![Airflow](https://img.shields.io/badge/Airflow-2.9-017CEE?logo=apacheairflow)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)

**[→ Streamlit App](https://brasilbid.streamlit.app)** · **[→ Power BI Dashboard](https://app.powerbi.com/view?r=eyJrIjoiYjQzNDdiMmMtMzczMi00MmY0LWIyZjMtMDg2NTEwNTUzZjE2IiwidCI6ImY5OTZjZmRiLTQyYWMtNGVhZC1iYzQzLThmZmY3Njc0Zjg4NiIsImMiOjR9&pageName=c90308a9d2662513e95b)** · **[→ API Docs](http://localhost:8000/docs)**

---

## O Problema

O governo federal publica **todas as compras públicas** no PNCP — licitações, contratos, dispensas — mas os dados ficam fragmentados em PDFs, portais lentos e sem nenhuma camada analítica. Empresas, fornecedores e cidadãos não têm como visualizar tendências, identificar oportunidades ou fiscalizar órgãos com eficiência.

**BrasilBid resolve isso com infraestrutura de dados real e atualização diária automática.**

---

## Screenshots

| Visão Geral — KPIs + Licitações por UF + Modalidades |
|:-----------------------------------------------------:|
| ![Visão Geral](screenshots/visao-geral.png) |

| Evolução Diária — Volume e Valor ao longo do tempo |
|:---------------------------------------------------:|
| ![Timeline](screenshots/timeline.png) |

| Ranking de Órgãos — Top 1.400+ entidades públicas |
|:-------------------------------------------------:|
| ![Ranking Órgãos](screenshots/ranking-orgaos.png) |

---

## Arquitetura

```
PNCP API (8 modalidades)
    │
    ▼
Python ETL (ingestion/)
    │  ├─ pncp.py       # cliente API, paginação, retry com backoff exponencial
    │  ├─ db.py         # DDL SQLAlchemy + engine
    │  └─ upsert.py     # batch upsert ON CONFLICT DO UPDATE
    ▼
PostgreSQL 17 (Neon serverless)
    │  └─ raw.contratacoes   # tabela raw, PK: numero_controle_pncp
    ▼
dbt (dbt/)
    │  ├─ staging/stg_licitacoes     # view limpa e tipada
    │  └─ mart/
    │       ├─ mart_por_uf           ├─ mart_por_municipio
    │       ├─ mart_por_modalidade   ├─ mart_timeline
    │       ├─ mart_ranking_orgaos   └─ mart_oportunidades
    ▼                                    ▼
FastAPI (api/)                   Streamlit (streamlit_app.py)
├─ GET /oportunidades            ├─ Visão Geral (KPIs + mapa UF)
├─ GET /municipios               ├─ Oportunidades Ativas
└─ GET /stats/resumo             ├─ Evolução Temporal
         /stats/por-uf           ├─ Ranking de Órgãos
         /stats/ranking-orgaos   └─ Power BI (embed)
    ▼
Apache Airflow (dags/brasilbid_pipeline.py)
    ingest_pncp → gen_dbt_profiles → dbt_run → dbt_test
    Agendado: 08:00 UTC (05:00 BRT) diariamente
    ▼
GitHub Actions (cron diário 05:00 BRT)
    ETL → dbt run → dbt test (18 testes automáticos)
```

---

## Números Reais

| Métrica | Valor |
|--------|-------|
| Total licitações | 2.700+ |
| Valor total estimado | R$ 8 Bi+ |
| Estados cobertos | 27 UFs |
| Órgãos públicos | 1.400+ |
| Atualização | Diária automática |
| Testes de qualidade | 18 dbt tests a cada execução |

---

## Stack

| Camada | Tecnologia | Decisão |
|--------|-----------|---------|
| Ingestão | Python 3.12 · requests · SQLAlchemy | upsert idempotente, retry com backoff exponencial |
| Warehouse | PostgreSQL 17 — Neon serverless | custo zero, índices em UF, modalidade e data |
| Transformação | dbt-postgres 1.10 — staging → mart | SQL versionado, testável, documentado |
| Qualidade | dbt test — not_null, unique, accepted_values | 18 testes automáticos a cada run |
| API REST | FastAPI + Uvicorn | /oportunidades, /municipios, /stats com Swagger |
| Orquestração | Apache Airflow (DAG) + GitHub Actions | DAG local + cron para deploy contínuo |
| Visualização | Streamlit (ao vivo) + Power BI (embed) | dashboard interativo + padrão corporativo BR |
| Containerização | Docker + docker-compose | docker compose up app/api/pipeline |

---

## Como Executar

### Com Docker (recomendado)

```bash
git clone https://github.com/Vortex11PTBR/brasilibid
cd brasilibid
cp .env.example .env  # adicionar DATABASE_URL do Neon

# Dashboard Streamlit (localhost:8501)
docker compose up app

# API FastAPI — Swagger em localhost:8000/docs
docker compose up api

# Pipeline ETL + dbt (execução única)
docker compose --profile pipeline run pipeline

# Airflow — UI em localhost:8080 (admin/admin)
docker compose -f docker-compose.airflow.yml up
```

### Local (Python)

```bash
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

python run_ingestion.py --days 7          # ingestão
python scripts/gen_profiles.py            # gera profiles dbt
dbt run  --project-dir dbt --profiles-dir dbt
dbt test --project-dir dbt --profiles-dir dbt
uvicorn api.main:app --reload             # FastAPI
streamlit run streamlit_app.py            # dashboard
```

---

## Estrutura

```
brasilibid/
├── api/
│   ├── main.py                 # FastAPI app, CORS, routers
│   ├── database.py             # engine pg8000 + SSL (Neon)
│   └── routers/
│       ├── oportunidades.py    # GET /oportunidades
│       ├── municipios.py       # GET /municipios
│       └── stats.py            # GET /stats/*
├── dags/
│   └── brasilbid_pipeline.py   # DAG Airflow (4 tasks)
├── ingestion/
│   ├── db.py                   # schema + engine PostgreSQL
│   ├── pncp.py                 # cliente PNCP API + retry
│   └── upsert.py               # batch upsert idempotente
├── dbt/
│   └── models/
│       ├── schema.yml          # 18 testes de qualidade
│       ├── staging/stg_licitacoes.sql
│       └── mart/               # 7 modelos mart
├── scripts/gen_profiles.py     # gera dbt/profiles.yml
├── screenshots/
├── .github/workflows/ingest.yml
├── Dockerfile                  # Streamlit
├── Dockerfile.api              # FastAPI
├── Dockerfile.pipeline         # ETL + dbt
├── Dockerfile.airflow          # Airflow + deps
├── docker-compose.yml
├── docker-compose.airflow.yml
├── run_ingestion.py
├── streamlit_app.py
└── requirements.txt
```

---

## Fonte de Dados

**PNCP — Portal Nacional de Contratações Públicas** (`api.compras.gov.br`), API oficial do governo federal.

| Código | Modalidade |
|--------|-----------|
| 1 | Leilão | 2 | Diálogo Competitivo | 3 | Concurso | 4 | Concorrência |
| 5 | Pregão | 6 | Manifestação de Interesse | 7 | Pré-qualificação | 8 | Credenciamento |

---

Desenvolvido por [João Lacerda](https://joaolacerda.dev) · Dados: PNCP / Portal Nacional de Contratações Públicas