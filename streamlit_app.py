"""
BrasilBid — Monitor de Licitações Públicas
App Streamlit com dados ao vivo do PNCP via PostgreSQL (Neon)
"""
import os
import re
import ssl

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
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
  /* ── Reset Streamlit clutter ── */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }
  [data-testid="stSidebar"] { background: #0d1117 !important; border-right: 1px solid #21262d; }
  [data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }

  /* ── Fundo geral ── */
  .stApp { background: #0d1117; }

  /* ── Hero header ── */
  .hero {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 60%, #0e2a3a 100%);
    border: 1px solid #21262d;
    border-radius: 14px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
  }
  .hero::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #00d4ff, transparent);
  }
  .hero-title {
    font-size: 1.8rem; font-weight: 800; color: #e6edf3;
    margin: 0 0 0.2rem 0; letter-spacing: -0.5px;
  }
  .hero-title span { color: #00d4ff; }
  .hero-sub { color: #8b949e; font-size: 0.9rem; margin: 0; }

  /* ── KPI Cards ── */
  .kpi-grid { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
  .kpi-card {
    flex: 1;
    background: linear-gradient(145deg, #161b22, #0d1117);
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, border-color 0.2s;
  }
  .kpi-card:hover { transform: translateY(-2px); border-color: #00d4ff44; }
  .kpi-card::after {
    content: '';
    position: absolute; bottom: 0; left: 50%; transform: translateX(-50%);
    width: 60%; height: 1px;
    background: linear-gradient(90deg, transparent, #00d4ff66, transparent);
  }
  .kpi-icon { font-size: 1.3rem; margin-bottom: 0.4rem; }
  .kpi-label { color: #8b949e; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 0.4rem; }
  .kpi-value {
    color: #00d4ff; font-size: 2rem; font-weight: 800;
    font-family: 'SF Mono', 'Fira Code', monospace;
    line-height: 1; margin-bottom: 0.3rem;
    text-shadow: 0 0 20px rgba(0,212,255,0.3);
  }
  .kpi-sub { color: #484f58; font-size: 0.72rem; }

  /* ── Section titles ── */
  .section-title {
    color: #e6edf3; font-size: 1rem; font-weight: 600;
    border-left: 3px solid #00d4ff;
    padding-left: 0.7rem; margin: 1.2rem 0 0.8rem 0;
  }

  /* ── Divider ── */
  .glow-divider {
    height: 1px; border: none;
    background: linear-gradient(90deg, transparent, #21262d 20%, #21262d 80%, transparent);
    margin: 1.2rem 0;
  }

  /* ── LIVE badge animado ── */
  @keyframes pulse-live { 0%,100%{opacity:1} 50%{opacity:0.5} }
  .live-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: #0d2119; color: #3fb950;
    border: 1px solid #2ea04344; border-radius: 20px;
    padding: 3px 10px; font-size: 0.72rem; font-weight: 700;
    letter-spacing: 0.5px;
  }
  .live-dot {
    width: 6px; height: 6px; background: #3fb950;
    border-radius: 50%; animation: pulse-live 1.5s infinite;
  }

  /* ── Sidebar brand ── */
  .sidebar-brand {
    text-align: center; padding: 0.5rem 0 1rem 0;
  }
  .sidebar-brand .brand-icon { font-size: 2.8rem; margin-bottom: 0.3rem; }
  .sidebar-brand .brand-name {
    font-size: 1.3rem; font-weight: 800; color: #e6edf3; letter-spacing: -0.5px;
  }
  .sidebar-brand .brand-tag { color: #8b949e; font-size: 0.78rem; margin-top: 2px; }
  .sidebar-info {
    background: #161b22; border: 1px solid #21262d; border-radius: 8px;
    padding: 0.8rem 1rem; margin: 0.8rem 0; font-size: 0.78rem; color: #8b949e;
  }
  .sidebar-info b { color: #c9d1d9; }
  .sidebar-links { display: flex; gap: 0.5rem; justify-content: center; margin-top: 1rem; }
  .sidebar-links a {
    flex: 1; text-align: center; padding: 0.5rem;
    background: #161b22; border: 1px solid #21262d; border-radius: 8px;
    color: #8b949e !important; font-size: 0.78rem; text-decoration: none !important;
    transition: border-color 0.2s, color 0.2s;
  }
  .sidebar-links a:hover { border-color: #00d4ff; color: #00d4ff !important; }

  /* ── Tabela de oportunidades ── */
  .op-table-wrap { overflow-x: auto; border-radius: 10px; border: 1px solid #21262d; }
  table.op-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
  table.op-table th {
    background: #161b22; color: #00d4ff;
    padding: 10px 12px; text-align: left; font-weight: 600;
    border-bottom: 2px solid #21262d; white-space: nowrap;
  }
  table.op-table td {
    padding: 9px 12px; border-bottom: 1px solid #161b22;
    color: #c9d1d9; vertical-align: middle;
  }
  table.op-table tr:hover td { background: #161b22cc; }
  table.op-table td:first-child { font-weight: 600; color: #00d4ff; }
  table.op-table a {
    color: #00d4ff; text-decoration: none;
    background: #0e2a3a; border: 1px solid #00d4ff44;
    padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;
  }
  table.op-table a:hover { background: #00d4ff22; }
  .warn-days { color: #f78166; font-weight: 600; }
  .ok-days { color: #3fb950; }

  /* ── Badges de count ── */
  .count-badge {
    display: inline-block;
    background: #0e2a3a; color: #00d4ff;
    border: 1px solid #00d4ff44; border-radius: 6px;
    padding: 4px 12px; font-size: 0.82rem; font-weight: 600;
    margin-right: 0.5rem;
  }
  .count-badge.green { background: #0d2119; color: #3fb950; border-color: #3fb95044; }
</style>
""", unsafe_allow_html=True)


# ── Conexão BD ────────────────────────────────────────────────────────────────
@st.cache_resource
def get_engine():
    url = st.secrets.get("DATABASE_URL") or os.environ.get("DATABASE_URL", "")
    if not url:
        st.error("❌ DATABASE_URL não configurado nas Secrets do Streamlit Cloud.")
        st.stop()
    # pg8000 não suporta esses parâmetros na URL — remover
    url = re.sub(r"[&?]channel_binding=[^&]*", "", url)
    url = re.sub(r"[&?]sslmode=[^&]*", "", url)
    # Dialeto pg8000 (puro Python, compatível com qualquer versão)
    url = url.replace("postgresql://", "postgresql+pg8000://", 1)
    url = url.replace("postgres://", "postgresql+pg8000://", 1)
    # SSL via contexto nativo Python (necessário para Neon)
    ssl_context = ssl.create_default_context()
    return create_engine(url, connect_args={"ssl_context": ssl_context})


@st.cache_data(ttl=3600, show_spinner="Carregando dados...")
def load_mart(table: str) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(f"SELECT * FROM public_mart.{table}", conn)


def fmt_brl(v) -> str:
    """Formata número como R$ 1.234.567"""
    if pd.isna(v):
        return "—"
    if v >= 1_000_000_000:
        return f"R$ {v/1_000_000_000:.1f} Bi"
    if v >= 1_000_000:
        return f"R$ {v/1_000_000:,.1f} Mi".replace(",", ".")
    return f"R$ {v:,.0f}".replace(",", ".")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
      <div class="brand-icon">🏛️</div>
      <div class="brand-name">BrasilBid</div>
      <div class="brand-tag">Monitor de Licitações Públicas</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div style="text-align:center;margin-bottom:1rem">'
        '<span class="live-badge"><span class="live-dot"></span>DADOS AO VIVO</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div class="sidebar-info">
      <b>📡 Fonte</b><br>PNCP — Portal Nacional de Contratações Públicas
    </div>
    <div class="sidebar-info">
      <b>🔄 Atualização</b><br>Diária às 05:00 BRT via GitHub Actions
    </div>
    <div class="sidebar-info">
      <b>🗄️ Stack</b><br>Python → PostgreSQL → dbt → Streamlit
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-links">
      <a href="https://github.com/Vortex11PTBR/brasilibid" target="_blank">⌥ GitHub</a>
      <a href="https://joaolacerda.dev" target="_blank">👤 Portfólio</a>
    </div>
    """, unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <p class="hero-title">Brasil<span>Bid</span></p>
  <p class="hero-sub">Monitor em tempo real de licitações públicas brasileiras — PNCP API</p>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊  Visão Geral",
    "🟢  Oportunidades Ativas",
    "📈  Evolução Temporal",
    "🏆  Ranking de Órgãos",
    "📑  Power BI",
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

    kpis = [
        ("📋", "Total de Licitações",  f"{total_lic:,}".replace(",","."), "publicadas no PNCP"),
        ("💰", "Valor Total Estimado", fmt_brl(valor_total),               "em contratos públicos"),
        ("🗺️", "Estados Cobertos",     str(total_ufs),                     "de 27 UFs brasileiras"),
        ("🏢", "Órgãos Públicos",      f"{total_orgaos:,}".replace(",","."), "entidades distintas"),
    ]
    cards_html = '<div class="kpi-grid">'
    for icon, label, val, sub in kpis:
        cards_html += (
            f'<div class="kpi-card">'
            f'<div class="kpi-icon">{icon}</div>'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{val}</div>'
            f'<div class="kpi-sub">{sub}</div>'
            f'</div>'
        )
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    st.markdown('<hr class="glow-divider">', unsafe_allow_html=True)
    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown('<p class="section-title">Licitações por Estado</p>', unsafe_allow_html=True)
        fig_uf = px.bar(
            df_uf.sort_values("total_licitacoes", ascending=True),
            x="total_licitacoes",
            y="uf_sigla",
            orientation="h",
            text="total_licitacoes",
            color="total_licitacoes",
            color_continuous_scale=[[0,"#0e2a3a"],[0.5,"#0077aa"],[1,"#00d4ff"]],
            labels={"total_licitacoes": "Licitações", "uf_sigla": ""},
        )
        fig_uf.update_traces(textposition="outside", textfont_size=10, marker_line_width=0)
        fig_uf.update_layout(
            showlegend=False, coloraxis_showscale=False,
            height=620, margin=dict(l=0, r=60, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#8b949e", xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(tickfont=dict(color="#c9d1d9", size=11)),
        )
        st.plotly_chart(fig_uf, use_container_width=True)

    with col_b:
        st.markdown('<p class="section-title">Por Modalidade</p>', unsafe_allow_html=True)
        fig_mod = px.pie(
            df_mod,
            values="total_licitacoes",
            names="modalidade_nome",
            hole=0.6,
            color_discrete_sequence=["#00d4ff","#0077aa","#005580","#003355","#001122"],
        )
        fig_mod.update_traces(
            textposition="inside", textinfo="percent",
            hovertemplate="<b>%{label}</b><br>%{value} licitações<br>%{percent}<extra></extra>",
            marker=dict(line=dict(color="#0d1117", width=2)),
        )
        fig_mod.update_layout(
            height=300, margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#c9d1d9", showlegend=True,
            legend=dict(font=dict(size=10, color="#8b949e"), orientation="v"),
        )
        st.plotly_chart(fig_mod, use_container_width=True)

        st.markdown('<p class="section-title">Valor por Modalidade</p>', unsafe_allow_html=True)
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
    st.markdown("""
    <div class="hero" style="padding:1rem 1.5rem;margin-bottom:1rem">
      <p style="color:#e6edf3;font-size:1rem;font-weight:700;margin:0">🟢 Oportunidades Ativas</p>
      <p style="color:#8b949e;font-size:0.8rem;margin:2px 0 0 0">
        Licitações com prazo de encerramento ainda não vencido · Atualizado diariamente
      </p>
    </div>
    """, unsafe_allow_html=True)

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
            f'<div style="margin:0.5rem 0 1rem 0">'
            f'<span class="count-badge">📋 {len(df_f):,} oportunidades</span>'
            f'<span class="count-badge green">💰 {fmt_brl(df_f["valor_estimado"].sum())}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        df_show = df_f[[
            "uf_sigla", "municipio_nome", "modalidade_nome", "orgao_nome",
            "objeto_compra", "valor_estimado", "data_encerramento",
            "dias_restantes", "link_edital",
        ]].copy()

        df_show["valor_estimado"] = df_show["valor_estimado"].apply(fmt_brl)
        def fmt_dias(d):
            if pd.isna(d): return "—"
            d = int(d)
            cls = "warn-days" if d <= 7 else "ok-days"
            ico = "⚠️ " if d <= 7 else ""
            return f'<span class="{cls}">{ico}{d}d</span>'
        df_show["dias_restantes"] = df_show["dias_restantes"].apply(fmt_dias)
        df_show["link_edital"] = df_show["link_edital"].apply(
            lambda u: f'<a href="{u}" target="_blank">↗ Edital</a>'
            if pd.notna(u) and str(u).startswith("http") else "—"
        )
        df_show = df_show.rename(columns={
            "uf_sigla": "UF", "municipio_nome": "Município",
            "modalidade_nome": "Modalidade", "orgao_nome": "Órgão",
            "objeto_compra": "Objeto", "valor_estimado": "Valor",
            "data_encerramento": "Encerra", "dias_restantes": "Dias",
            "link_edital": "Link",
        })

        st.markdown(
            '<div class="op-table-wrap">'
            + df_show.to_html(escape=False, index=False, classes="op-table")
            + '</div>',
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Evolução Temporal
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<p class="section-title">📈 Evolução Temporal</p>', unsafe_allow_html=True)

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
    st.markdown('<p class="section-title">🏆 Ranking de Órgãos</p>', unsafe_allow_html=True)

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
        st.markdown('<p class="section-title">Por valor total estimado</p>', unsafe_allow_html=True)
        df_val_top = df_org_f.nlargest(15, "valor_total_estimado")[
            ["orgao_nome", "uf_sigla", "valor_total_estimado", "total_licitacoes"]
        ].copy()
        df_val_top["valor_total_estimado"] = df_val_top["valor_total_estimado"].apply(fmt_brl)
        df_val_top.columns = ["Órgão", "UF", "Valor Total", "Licitações"]
        st.dataframe(df_val_top, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Power BI
# ═══════════════════════════════════════════════════════════════════════════════
POWERBI_URL = (
    "https://app.powerbi.com/view?r=eyJrIjoiYjQzNDdiMmMtMzczMi00MmY0LWIyZjMtMDg2NTEwNTUzZjE2Iiwidci"
    "I6ImY5OTZjZmRiLTQyYWMtNGVhZC1iYzQzLThmZmY3Njc0Zjg4NiIsImMiOjR9&pageName=c90308a9d2662513e95b"
)

with tab5:
    st.markdown("""
    <div class="hero" style="padding:1rem 1.5rem;margin-bottom:1rem">
      <p style="color:#e6edf3;font-size:1rem;font-weight:700;margin:0">📑 Dashboard Power BI</p>
      <p style="color:#8b949e;font-size:0.8rem;margin:2px 0 0 0">
        Relatório interativo com visões de UF, modalidade, órgão e evolução temporal · DAX + Power Query
      </p>
    </div>
    """, unsafe_allow_html=True)

    components.iframe(POWERBI_URL, height=700, scrolling=True)

    st.markdown(
        f'<div style="text-align:center;margin-top:0.5rem">'
        f'<a href="{POWERBI_URL}" target="_blank" style="color:#8b949e;font-size:0.78rem;'
        f'text-decoration:none;border:1px solid #21262d;border-radius:6px;padding:4px 12px;">'
        f'↗ Abrir em tela cheia</a></div>',
        unsafe_allow_html=True,
    )
