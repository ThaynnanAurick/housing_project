import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# -------------------------
# CARREGAMENTO DOS DADOS
# -------------------------
@st.cache_data
def load_data():
    return pd.read_csv("perda_poder_compra_habitacao_2018_2025.csv")

df = load_data()

st.title("Perda de Poder de Compra Habitacional (2018–2025)")

# -------------------------
# FILTROS
# -------------------------
country = st.selectbox("Selecione o país", df["country"].unique())

year_min = int(df["year"].min())
year_max = int(df["year"].max())

year_range = st.slider(
    "Selecione o intervalo de anos",
    year_min,
    year_max,
    (year_min, year_max)
)

filtered_df = df[
    (df["country"] == country) &
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
].copy()

# -------------------------
# MÉTRICAS DERIVADAS
# -------------------------

filtered_df["housing_effort_years"] = (
    (filtered_df["avg_house_price_per_m2_usd"] * 100)
    / filtered_df["average_salary_usd"]
)

filtered_df["real_salary"] = (
    filtered_df["average_salary_usd"]
    / (1 + filtered_df["inflation_rate_percent"] / 100)
)

filtered_df["interest_pressure"] = (
    filtered_df["interest_rate_percent"]
    * filtered_df["avg_house_price_per_m2_usd"]
)

# -------------------------
# KPIs
# -------------------------
st.subheader("Indicadores Principais")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Anos para comprar 100m² (último ano)",
    round(filtered_df["housing_effort_years"].iloc[-1], 2)
)

col2.metric(
    "Inflação (último ano)",
    f'{filtered_df["inflation_rate_percent"].iloc[-1]} %'
)

col3.metric(
    "Taxa de Juros (último ano)",
    f'{filtered_df["interest_rate_percent"].iloc[-1]} %'
)

# -------------------------
# GRÁFICOS
# -------------------------
st.subheader("Evolução do Poder de Compra")

fig1 = px.line(
    filtered_df,
    x="year",
    y="housing_effort_years",
    markers=True
)

st.plotly_chart(fig1, use_container_width=True)

fig2 = px.line(
    filtered_df,
    x="year",
    y="real_salary",
    markers=True
)

st.plotly_chart(fig2, use_container_width=True)

fig3 = px.line(
    filtered_df,
    x="year",
    y="interest_pressure",
    markers=True
)

st.plotly_chart(fig3, use_container_width=True)

# -------------------------
# ANÁLISE AUTOMÁTICA
# -------------------------
st.subheader("Análise Automática")

first = filtered_df["housing_effort_years"].iloc[0]
last = filtered_df["housing_effort_years"].iloc[-1]

if last > first:
    st.error("O poder de compra piorou no período selecionado.")
else:
    st.success("O poder de compra melhorou no período selecionado.")
