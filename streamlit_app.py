"""
BrasilBid — Monitor de Licitações Públicas
App Streamlit com dados ao vivo do PNCP via PostgreSQL (Neon)
"""
import os

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

# ── Configuração da página ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="BrasilBid — Licitações Públicas",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .kpi-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    margin-bottom: 1rem;
  }
  .kpi-label { color: #8b949e; font-size: 0.82rem; margin-bottom: 4px; }
  .kpi-value { color: #00d4ff; font-size: 1.9rem; font-weight: 700; font-family: monospace; }
  .kpi-sub   { color: #6e7681; font-size: 0.75rem; margin-top: 2px; }

  /* Tabela de oportunidades */
  table.dataframe { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
  table.dataframe th {
    background: #21262d; color: #00d4ff;
    padding: 8px 10px; text-align: left; font-weight: 600;
    border-bottom: 2px solid #30363d;
  }
  table.dataframe td {
    padding: 7px 10px; border-bottom: 1px solid #21262d; color: #c9d1d9;
    vertical-align: top;
  }
  table.dataframe tr:hover td { background: #1c2128; }
  table.dataframe a { color: #00d4ff; text-decoration: none; }
  table.dataframe a:hover { text-decoration: underline; }

  /* Tag verde de live */
  .live-badge {
    display: inline-block;
    background: #1a4731; color: #3fb950;
    border: 1px solid #2ea043; border-radius: 20px;
    padding: 2px 10px; font-size: 0.78rem; font-weight: 600;
    margin-left: 8px;
  }
</style>
""", unsafe_allow_html=True)


# ── Conexão BD ────────────────────────────────────────────────────────────────
@st.cache_resource
def get_engine():
    # Streamlit Cloud secrets têm prioridade; fallback para env var local
    url = st.secrets.get("DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not url:
        st.error("❌ DATABASE_URL não configurado. Vá em Settings → Secrets e adicione a variável.")
        st.stop()
    url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    url = url.replace("postgres://", "postgresql+psycopg://", 1)
    return create_engine(url, pool_pre_ping=True)


@st.cache_data(ttl=3600, show_spinner="Carregando dados...")
def load_mart(table: str) -> pd.DataFrame:
    try:
        with get_engine().connect() as conn:
            return pd.read_sql(f"SELECT * FROM public_mart.{table}", conn)
    except Exception as e:
        st.error(f"❌ Erro ao carregar `{table}`: {e}")
        st.stop()


def fmt_brl(v) -> str:
    """Formata número como R$ 1.234.567"""
    if pd.isna(v):
        return "—"
    if v >= 1_000_000:
        return f"R$ {v/1_000_000:.1f} Mi"
    return f"R$ {v:,.0f}".replace(",", ".")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏛️ BrasilBid")
    st.markdown("Monitor de Licitações Públicas")
    st.markdown('<span class="live-badge">● LIVE</span>', unsafe_allow_html=True)
    st.divider()
    st.caption("📡 Fonte: PNCP — Portal Nacional de Contratações Públicas")
    st.caption("🔄 Atualização: diária às 05:00 BRT (GitHub Actions)")
    st.divider()
    st.markdown(
        "[🔗 GitHub](https://github.com/Vortex11PTBR/brasilibid) &nbsp;·&nbsp; "
        "[👨‍💻 Portfólio](https://joaolacerda.dev)",
        unsafe_allow_html=True,
    )


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Visão Geral",
    "🟢  Oportunidades Ativas",
    "📈  Evolução Temporal",
    "🏆  Ranking de Órgãos",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Visão Geral
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    df_uf  = load_mart("mart_por_uf")
    df_mod = load_mart("mart_por_modalidade")

    total_lic    = int(df_uf["total_licitacoes"].sum())
    valor_total  = float(df_uf["valor_total_estimado"].sum())
    total_ufs    = int(df_uf["uf_sigla"].nunique())
    total_orgaos = int(df_uf["total_orgaos"].sum())

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, sub in [
        (c1, "Total de Licitações",   f"{total_lic:,}".replace(",", "."),     "publicadas no PNCP"),
        (c2, "Valor Total Estimado",  fmt_brl(valor_total),                   "em contratos públicos"),
        (c3, "Estados Cobertos",      str(total_ufs),                         "de 27 UFs brasileiros"),
        (c4, "Órgãos Públicos",       f"{total_orgaos:,}".replace(",", "."),  "entidades distintas"),
    ]:
        col.markdown(
            f'<div class="kpi-card">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{val}</div>'
            f'<div class="kpi-sub">{sub}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown("#### Licitações por Estado")
        fig_uf = px.bar(
            df_uf.sort_values("total_licitacoes", ascending=True),
            x="total_licitacoes",
            y="uf_sigla",
            orientation="h",
            text="total_licitacoes",
            color="total_licitacoes",
            color_continuous_scale="Blues",
            labels={"total_licitacoes": "Licitações", "uf_sigla": "UF"},
        )
        fig_uf.update_traces(textposition="outside", textfont_size=11)
        fig_uf.update_layout(
            showlegend=False, coloraxis_showscale=False,
            height=600, margin=dict(l=0, r=60, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#c9d1d9",
        )
        st.plotly_chart(fig_uf, use_container_width=True)

    with col_b:
        st.markdown("#### Por Modalidade")
        fig_mod = px.pie(
            df_mod,
            values="total_licitacoes",
            names="modalidade_nome",
            hole=0.5,
            color_discrete_sequence=px.colors.sequential.Blues_r,
        )
        fig_mod.update_traces(textposition="inside", textinfo="percent+label")
        fig_mod.update_layout(
            height=380, margin=dict(l=0, r=0, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#c9d1d9", showlegend=False,
        )
        st.plotly_chart(fig_mod, use_container_width=True)

        st.markdown("#### Valor por Modalidade")
        df_mod_val = df_mod.sort_values("valor_total_estimado", ascending=False)
        df_mod_val["valor_fmt"] = df_mod_val["valor_total_estimado"].apply(fmt_brl)
        st.dataframe(
            df_mod_val[["modalidade_nome", "total_licitacoes", "valor_fmt"]]
            .rename(columns={"modalidade_nome": "Modalidade",
                              "total_licitacoes": "Qtd",
                              "valor_fmt": "Valor Total"}),
            use_container_width=True, hide_index=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Oportunidades Ativas
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## 🟢 Oportunidades Ativas")
    st.caption(
        "Licitações com prazo de encerramento ainda não vencido. "
        "Use para identificar contratos em aberto. Atualizado diariamente."
    )

    df_op = load_mart("mart_oportunidades")

    if df_op.empty:
        st.info("Nenhuma oportunidade ativa no momento. O pipeline roda diariamente às 05:00 BRT.")
    else:
        f1, f2, f3, f4 = st.columns(4)
        ufs  = ["Todas"] + sorted(df_op["uf_sigla"].dropna().unique().tolist())
        mods = ["Todas"] + sorted(df_op["modalidade_nome"].dropna().unique().tolist())

        uf_sel   = f1.selectbox("Estado (UF)", ufs)
        mod_sel  = f2.selectbox("Modalidade", mods)
        dias_max = f3.slider("Encerra em até (dias)", 1, 365, 90)
        val_min  = f4.number_input("Valor mínimo (R$)", min_value=0, value=0, step=10000)

        df_f = df_op.copy()
        if uf_sel  != "Todas": df_f = df_f[df_f["uf_sigla"] == uf_sel]
        if mod_sel != "Todas": df_f = df_f[df_f["modalidade_nome"] == mod_sel]
        df_f = df_f[df_f["dias_restantes"].fillna(999) <= dias_max]
        df_f = df_f[df_f["valor_estimado"].fillna(0) >= val_min]

        st.markdown(
            f"**{len(df_f):,} oportunidades** encontradas "
            f"| Valor total: **{fmt_brl(df_f['valor_estimado'].sum())}**"
        )

        df_show = df_f[[
            "uf_sigla", "municipio_nome", "modalidade_nome", "orgao_nome",
            "objeto_compra", "valor_estimado", "data_encerramento",
            "dias_restantes", "link_edital",
        ]].copy()

        df_show["valor_estimado"] = df_show["valor_estimado"].apply(fmt_brl)
        df_show["dias_restantes"] = df_show["dias_restantes"].apply(
            lambda d: f"⚠️ {int(d)}d" if pd.notna(d) and int(d) <= 7
            else (f"{int(d)}d" if pd.notna(d) else "—")
        )
        df_show["link_edital"] = df_show["link_edital"].apply(
            lambda u: f'<a href="{u}" target="_blank">🔗 Abrir</a>'
            if pd.notna(u) and str(u).startswith("http") else "—"
        )
        df_show = df_show.rename(columns={
            "uf_sigla": "UF", "municipio_nome": "Município",
            "modalidade_nome": "Modalidade", "orgao_nome": "Órgão",
            "objeto_compra": "Objeto", "valor_estimado": "Valor",
            "data_encerramento": "Encerra", "dias_restantes": "Dias",
            "link_edital": "Edital",
        })

        st.markdown(
            df_show.to_html(escape=False, index=False, classes="dataframe"),
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Evolução Temporal
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## Evolução Temporal")

    df_tl = load_mart("mart_timeline")
    df_tl["data_publicacao"] = pd.to_datetime(df_tl["data_publicacao"])

    modalidades_tl = ["Todas"] + sorted(df_tl["modalidade_nome"].dropna().unique().tolist())
    mod_tl = st.selectbox("Filtrar por modalidade", modalidades_tl)

    df_f_tl = df_tl if mod_tl == "Todas" else df_tl[df_tl["modalidade_nome"] == mod_tl]
    df_agg = (
        df_f_tl.groupby("data_publicacao")
        .agg(total_licitacoes=("total_licitacoes", "sum"),
             valor_total=("valor_total_estimado", "sum"))
        .reset_index()
    )

    col_l, col_r = st.columns(2)
    _layout = dict(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#c9d1d9", margin=dict(t=40, b=20, l=10, r=10),
    )

    with col_l:
        fig_cnt = px.line(
            df_agg, x="data_publicacao", y="total_licitacoes",
            title="Licitações publicadas por dia",
            labels={"data_publicacao": "Data", "total_licitacoes": "Quantidade"},
            color_discrete_sequence=["#00d4ff"],
        )
        fig_cnt.update_traces(line_width=2, fill="tozeroy", fillcolor="rgba(0,212,255,0.08)")
        fig_cnt.update_layout(**_layout)
        st.plotly_chart(fig_cnt, use_container_width=True)

    with col_r:
        fig_val = px.area(
            df_agg, x="data_publicacao", y="valor_total",
            title="Valor estimado publicado por dia (R$)",
            labels={"data_publicacao": "Data", "valor_total": "Valor (R$)"},
            color_discrete_sequence=["#3fb950"],
        )
        fig_val.update_layout(**_layout)
        st.plotly_chart(fig_val, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Ranking de Órgãos
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("## Ranking de Órgãos")

    df_org = load_mart("mart_por_orgao")

    f_a, f_b = st.columns(2)
    ufs_org = ["Todos"] + sorted(df_org["uf_sigla"].dropna().unique().tolist())
    uf_org = f_a.selectbox("Filtrar por UF", ufs_org)
    top_n  = f_b.slider("Top N órgãos", 10, 50, 20)

    df_org_f   = df_org if uf_org == "Todos" else df_org[df_org["uf_sigla"] == uf_org]
    df_org_top = df_org_f.nlargest(top_n, "total_licitacoes")

    col_l2, col_r2 = st.columns([3, 2])

    with col_l2:
        fig_org = px.bar(
            df_org_top.sort_values("total_licitacoes", ascending=True),
            x="total_licitacoes",
            y="orgao_nome",
            orientation="h",
            color="total_licitacoes",
            color_continuous_scale="Teal",
            labels={"total_licitacoes": "Licitações", "orgao_nome": "Órgão"},
            title=f"Top {top_n} órgãos por volume de licitações",
        )
        fig_org.update_layout(
            showlegend=False, coloraxis_showscale=False,
            height=max(420, top_n * 24),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#c9d1d9", margin=dict(l=0, r=20, t=40, b=10),
        )
        st.plotly_chart(fig_org, use_container_width=True)

    with col_r2:
        st.markdown("#### Por valor total estimado")
        df_val_top = df_org_f.nlargest(15, "valor_total_estimado")[
            ["orgao_nome", "uf_sigla", "valor_total_estimado", "total_licitacoes"]
        ].copy()
        df_val_top["valor_total_estimado"] = df_val_top["valor_total_estimado"].apply(fmt_brl)
        df_val_top.columns = ["Órgão", "UF", "Valor Total", "Licitações"]
        st.dataframe(df_val_top, use_container_width=True, hide_index=True)
