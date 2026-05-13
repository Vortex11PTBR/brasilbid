# 🏛️ BrasilBid — Monitor de Licitações Públicas

> ETL pipeline ingesting Brazil's public procurement data from the PNCP API → PostgreSQL → dbt → Power BI live dashboard.

[![Live Dashboard](https://img.shields.io/badge/Power%20BI-Live%20Dashboard-yellow?logo=powerbi)](https://app.powerbi.com/view?r=eyJrIjoiYjQzNDdiMmMtMzczMi00MmY0LWIyZjMtMDg2NTEwNTUzZjE2IiwidCI6ImY5OTZjZmRiLTQyYWMtNGVhZC1iYzQzLThmZmY3Njc0Zjg4NiIsImMiOjR9&pageName=c90308a9d2662513e95b)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-blue?logo=githubactions)](https://github.com/Vortex11PTBR/brasilibid/actions)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![dbt](https://img.shields.io/badge/dbt-1.10-orange?logo=dbt)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue?logo=postgresql)

## 📊 Live Dashboard

**[→ Open Power BI Dashboard](https://app.powerbi.com/view?r=eyJrIjoiYjQzNDdiMmMtMzczMi00MmY0LWIyZjMtMDg2NTEwNTUzZjE2IiwidCI6ImY5OTZjZmRiLTQyYWMtNGVhZC1iYzQzLThmZmY3Njc0Zjg4NiIsImMiOjR9&pageName=c90308a9d2662513e95b)**

4 pages covering R$ 8B+ in public procurement:
- **Visão Geral** — KPIs, licitações by UF, modality breakdown
- **Análise Temporal** — Daily publication trends
- **Ranking de Órgãos** — Top 1,400+ government entities by volume
- **Licitações Recentes** — Interactive table with UF + modality filters

## 🏗️ Architecture

```
PNCP API (8 modalities)
    │
    ▼
Python ETL (ingestion/)
    │  ├─ pncp.py       # API client, pagination, rate limiting
    │  ├─ db.py         # SQLAlchemy DDL + engine
    │  └─ upsert.py     # Batch upsert ON CONFLICT DO UPDATE
    ▼
PostgreSQL (Neon serverless)
    │  └─ licitacoes    # Raw table, PK: numero_controle_pncp
    ▼
dbt (dbt/)
    │  ├─ staging/stg_licitacoes        # Cleaned view
    │  └─ mart/
    │       ├─ mart_por_uf              # By state
    │       ├─ mart_por_modalidade      # By modality
    │       ├─ mart_por_orgao           # Top entities
    │       ├─ mart_timeline            # Daily series
    │       └─ mart_recentes            # Last 500 bids
    ▼
Power BI Desktop → Publish to Web (public embed)
    │
    ▼
GitHub Actions (daily cron 05:00 BRT)
```

## 📈 Current Stats

| Metric | Value |
|--------|-------|
| Total licitações | 2,700+ |
| Total value | R$ 8B+ |
| States covered | 27 UFs |
| Government entities | 1,400+ |
| Update frequency | Daily |

## 🚀 Getting Started

### Prerequisites

```bash
python >= 3.12
dbt-postgres >= 1.10
```

### Installation

```bash
git clone https://github.com/Vortex11PTBR/brasilibid
cd brasilibid
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
# Edit .env with your DATABASE_URL
```

### Run ETL

```bash
# Ingest last 7 days
python run_ingestion.py --days 7

# Ingest specific date
python run_ingestion.py --date 2026-05-01
```

### Run dbt

```bash
cd dbt
dbt debug --profiles-dir .
dbt run --profiles-dir .
```

## 🗄️ Data Source

Data from **PNCP — Portal Nacional de Contratações Públicas** (`api.compras.gov.br`), the official Brazilian public procurement API.

Modalities covered:
| Code | Name |
|------|------|
| 1 | Leilão |
| 2 | Diálogo Competitivo |
| 3 | Concurso |
| 4 | Concorrência |
| 5 | Pregão |
| 6 | Manifestação de Interesse |
| 7 | Pré-qualificação |
| 8 | Credenciamento |

## 📁 Project Structure

```
brasilibid/
├── ingestion/
│   ├── db.py          # Database schema + engine
│   ├── pncp.py        # PNCP API client
│   └── upsert.py      # Batch upsert logic
├── dbt/
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── staging/
│   │   └── mart/
│   └── schema.yml
├── .github/
│   └── workflows/
│       └── ingest.yml  # Daily cron
├── run_ingestion.py
└── requirements.txt
```

## ⚙️ GitHub Actions

The pipeline runs automatically every day at 05:00 BRT via GitHub Actions. Set the `DATABASE_URL` secret in your repo settings.

## 🛠️ Tech Stack

- **Python 3.12** — ETL ingestion
- **PostgreSQL 17** (Neon serverless) — Data warehouse
- **dbt-postgres 1.10** — Data transformation + mart models
- **Power BI** — Dashboard + Publish to Web
- **GitHub Actions** — Daily orchestration
- **SQLAlchemy** — ORM + DDL
- **PNCP API** — Official Brazilian government procurement data

## 👨‍💻 Author

**João Pedro Lacerda** — [joaolacerda.dev](https://joaolacerda.dev) · [LinkedIn](https://www.linkedin.com/in/jo%C3%A3o-pedro-6575551b0)
