import pandas as pd
import streamlit as st
import altair as alt
import os
from vega_datasets import data

st.set_page_config(layout="wide")

st.title("🌍 Poder de Compra e Habitação (2018–2025)")

# ================================
# CARREGAR DADOS
# ================================

@st.cache_data
def load_data():

    caminho = os.path.expanduser("~/Desktop/perda_poder_compra_habitacao_2018_2025.csv")

    try:
        df = pd.read_csv(caminho)
    except:
        st.error("❌ Erro ao carregar o CSV. Verifique o caminho do arquivo.")
        st.stop()

    return df


df = load_data()

# garantir tipos corretos
df["ano"] = df["ano"].astype(int)

st.success(f"Dados carregados com sucesso: {df.shape[0]} linhas")

# ================================
# MAPA INTERATIVO
# ================================

st.subheader("🌎 Clique no país para filtrar os dados")

world = alt.topo_feature(data.world_110m.url, "countries")

# seleção de países
seleciona_pais = alt.selection_point(
    fields=["name"],
    toggle=True
)

mapa = (
    alt.Chart(world)
    .mark_geoshape(
        stroke="black"
    )
    .encode(
        color=alt.condition(
            seleciona_pais,
            alt.value("steelblue"),
            alt.value("lightgray")
        ),
        tooltip=[
            alt.Tooltip("name:N", title="País")
        ]
    )
    .add_params(seleciona_pais)
    .project("naturalEarth1")
    .properties(
        height=500
    )
)

st.altair_chart(mapa, use_container_width=True)

# ================================
# FILTROS
# ================================

st.subheader("Filtros")

col1, col2 = st.columns(2)

with col1:

    ano_inicio, ano_fim = st.select_slider(
        "Selecione o período:",
        options=sorted(df["ano"].unique()),
        value=(df["ano"].min(), df["ano"].max())
    )

paises = st.multiselect(
    "Países selecionados",
    options=sorted(df["pais"].unique()),
    default=[]
)

# aplicar filtros
df_filtrado = df[
    (df["ano"] >= ano_inicio) &
    (df["ano"] <= ano_fim)
]

if paises:
    df_filtrado = df_filtrado[df_filtrado["pais"].isin(paises)]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

# ================================
# GRÁFICOS
# ================================

st.subheader("📊 Indicadores Econômicos")

col1, col2 = st.columns(2)

# PREÇO HABITAÇÃO
with col1:

    st.markdown("### 🏠 Preço Médio da Habitação")

    grafico_preco = (
        alt.Chart(df_filtrado)
        .mark_line(point=True)
        .encode(
            x="ano:O",
            y="preco_medio_habitacao_usd:Q",
            color="pais:N",
            tooltip=["pais", "ano", "preco_medio_habitacao_usd"]
        )
        .interactive()
    )

    st.altair_chart(grafico_preco, use_container_width=True)

# INFLAÇÃO
with col2:

    st.markdown("### 📊 Inflação Anual (%)")

    grafico_inflacao = (
        alt.Chart(df_filtrado)
        .mark_line(point=True)
        .encode(
            x="ano:O",
            y="inflacao_anual_pct:Q",
            color="pais:N",
            tooltip=["pais", "ano", "inflacao_anual_pct"]
        )
        .interactive()
    )

    st.altair_chart(grafico_inflacao, use_container_width=True)

# ================================
# SEGUNDA LINHA
# ================================

col3, col4 = st.columns(2)

# SALÁRIO
with col3:

    st.markdown("### 💰 Salário Médio")

    grafico_salario = (
        alt.Chart(df_filtrado)
        .mark_line(point=True)
        .encode(
            x="ano:O",
            y="salario_medio_anual_usd:Q",
            color="pais:N",
            tooltip=["pais", "ano", "salario_medio_anual_usd"]
        )
        .interactive()
    )

    st.altair_chart(grafico_salario, use_container_width=True)

# ACESSIBILIDADE
with col4:

    st.markdown("### 📉 Acessibilidade Habitacional")

    grafico_ratio = (
        alt.Chart(df_filtrado)
        .mark_line(point=True)
        .encode(
            x="ano:O",
            y="preco_rendimento_ratio:Q",
            color="pais:N",
            tooltip=["pais", "ano", "preco_rendimento_ratio"]
        )
        .interactive()
    )

    st.altair_chart(grafico_ratio, use_container_width=True)