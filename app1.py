import pandas as pd
import streamlit as st
import altair as alt
from vega_datasets import data

st.title("🌍 Poder de Compra e Habitação (2018–2025)")

# ================================
# Carregar dados
# ================================

@st.cache_data
def load_data():
    caminho = "perda_poder_compra_habitacao_2018_2025.csv"
    df = pd.read_csv(caminho)
    return df

df = load_data()

st.write("✅ Dados carregados:", df.shape[0], "linhas")

# ================================
# FILTROS
# ================================

ano_inicio, ano_fim = st.select_slider(
"Selecione o período:",
options=sorted(df["ano"].unique()),
value=(df["ano"].min(), df["ano"].max())
)

df_filtrado = df[(df["ano"] >= ano_inicio) & (df["ano"] <= ano_fim)]

paises = st.multiselect(
"Selecione os países:",
df_filtrado["pais"].unique(),
default=df_filtrado["pais"].unique()
)

df_filtrado = df_filtrado[df_filtrado["pais"].isin(paises)]

# ================================
# GRÁFICO PREÇO HABITAÇÃO
# ================================

st.subheader("🏠 Evolução do Preço Médio da Habitação")

grafico_preco = alt.Chart(df_filtrado).mark_line(point=True).encode(
x="ano:O",
y="preco_medio_habitacao_usd:Q",
color="pais:N",
tooltip=["pais", "ano", "preco_medio_habitacao_usd"]
).properties(
height=400
).interactive()

st.altair_chart(grafico_preco, use_container_width=True)

# ================================
# INFLAÇÃO
# ================================

st.subheader("📊 Evolução da Inflação Anual (%)")

grafico_inflacao = alt.Chart(df_filtrado).mark_line(point=True).encode(
x="ano:O",
y="inflacao_anual_pct:Q",
color="pais:N",
tooltip=["pais", "ano", "inflacao_anual_pct"]
).interactive()

st.altair_chart(grafico_inflacao, use_container_width=True)

# ================================
# SALÁRIO
# ================================

st.subheader("💰 Evolução do Salário Médio")

grafico_salario = alt.Chart(df_filtrado).mark_line(point=True).encode(
x="ano:O",
y="salario_medio_anual_usd:Q",
color="pais:N",
tooltip=["pais", "ano", "salario_medio_anual_usd"]
).interactive()

st.altair_chart(grafico_salario, use_container_width=True)

# ================================
# ACESSIBILIDADE HABITACIONAL
# ================================

st.subheader("📉 Indicador de Acessibilidade Habitacional")

grafico_ratio = alt.Chart(df_filtrado).mark_line(point=True).encode(
x="ano:O",
y="preco_rendimento_ratio:Q",
color="pais:N",
tooltip=["pais", "ano", "preco_rendimento_ratio"]
).interactive()

st.altair_chart(grafico_ratio, use_container_width=True)

# ================================
# MAPA
# ================================

st.subheader("🌎 Países analisados")

world = alt.topo_feature(data.world_110m.url, "countries")

mapa = alt.Chart(world).mark_geoshape(
stroke="black"
).encode(
tooltip=["name:N"]
).project(
"naturalEarth1"
).properties(
width=1000,
height=500
)

st.altair_chart(mapa, use_container_width=True)