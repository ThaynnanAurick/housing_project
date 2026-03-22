import altair as alt
import pandas as pd
import streamlit as st

CSV_PATH = "perda_poder_compra_habitacao_2018_2025.csv"
APP_TITLE = "Poder de Compra e Habitacao"

METRIC_CARDS = [
    ("preco_medio_habitacao_usd", "Preco medio da habitacao (USD)"),
    ("salario_medio_anual_usd", "Salario medio anual (USD)"),
    ("inflacao_anual_pct", "Inflacao anual (%)"),
    ("preco_rendimento_ratio", "Relacao preco/rendimento"),
]


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype(int)
    return df.sort_values(["pais", "ano"]).reset_index(drop=True)


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()

    enriched["variacao_preco_pct"] = (
        enriched.groupby("pais")["preco_medio_habitacao_usd"].pct_change() * 100
    )
    enriched["variacao_salario_pct"] = (
        enriched.groupby("pais")["salario_medio_anual_usd"].pct_change() * 100
    )
    enriched["pressao_compra_pct"] = (
        enriched["variacao_preco_pct"] - enriched["variacao_salario_pct"]
    )

    inflation_factor = 1 + enriched["inflacao_anual_pct"] / 100
    enriched["indice_inflacao"] = inflation_factor.groupby(enriched["pais"]).cumprod()
    enriched["salario_real_indexado"] = (
        enriched["salario_medio_anual_usd"] / enriched["indice_inflacao"]
    )

    base_real_salary = enriched.groupby("pais")["salario_real_indexado"].transform("first")
    enriched["indice_salario_real_base100"] = (
        enriched["salario_real_indexado"] / base_real_salary * 100
    )

    base_ratio = enriched.groupby("pais")["preco_rendimento_ratio"].transform("first")
    enriched["piora_acessibilidade_pct"] = (
        (enriched["preco_rendimento_ratio"] / base_ratio) - 1
    ) * 100

    return enriched


def filter_data(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], tuple[int, int]]:
    st.sidebar.header("Filtros")

    years = sorted(df["ano"].unique().tolist())
    year_range = st.sidebar.select_slider(
        "Periodo",
        options=years,
        value=(years[0], years[-1]),
    )

    filtered = df[df["ano"].between(year_range[0], year_range[1])].copy()
    countries = sorted(filtered["pais"].unique().tolist())
    selected_countries = st.sidebar.multiselect(
        "Paises",
        options=countries,
        default=countries,
    )

    filtered = filtered[filtered["pais"].isin(selected_countries)].copy()
    return filtered, selected_countries, year_range


def build_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    ordered = df.sort_values(["pais", "ano"])
    summary = (
        ordered.groupby("pais")
        .agg(
            preco_inicial=("preco_medio_habitacao_usd", "first"),
            preco_final=("preco_medio_habitacao_usd", "last"),
            salario_inicial=("salario_medio_anual_usd", "first"),
            salario_final=("salario_medio_anual_usd", "last"),
            ratio_inicial=("preco_rendimento_ratio", "first"),
            ratio_final=("preco_rendimento_ratio", "last"),
            inflacao_media=("inflacao_anual_pct", "mean"),
            salario_real_base100_final=("indice_salario_real_base100", "last"),
        )
        .reset_index()
    )

    summary["alta_preco_pct"] = (
        (summary["preco_final"] / summary["preco_inicial"]) - 1
    ) * 100
    summary["alta_salario_pct"] = (
        (summary["salario_final"] / summary["salario_inicial"]) - 1
    ) * 100
    summary["piora_ratio_pct"] = (
        (summary["ratio_final"] / summary["ratio_inicial"]) - 1
    ) * 100
    summary["gap_preco_salario_pct"] = (
        summary["alta_preco_pct"] - summary["alta_salario_pct"]
    )
    summary["perda_salario_real_pct"] = 100 - summary["salario_real_base100_final"]

    return summary.sort_values("gap_preco_salario_pct", ascending=False)


def render_header(df: pd.DataFrame, summary: pd.DataFrame, year_range: tuple[int, int]) -> None:
    st.title(APP_TITLE)
    st.caption(
        "Como os paises vem perdendo poder de compra: quando o preco da habitacao sobe mais rapido que os salarios, "
        "e a inflacao reduz o ganho real."
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Paises analisados", df["pais"].nunique())
    col2.metric("Periodo", f"{year_range[0]} - {year_range[1]}")
    col3.metric(
        "Maior gap preco vs salario",
        f"{summary.iloc[0]['gap_preco_salario_pct']:.1f}%",
        summary.iloc[0]["pais"],
    )
    col4.metric(
        "Maior piora de acessibilidade",
        f"{summary['piora_ratio_pct'].max():.1f}%",
        summary.loc[summary["piora_ratio_pct"].idxmax(), "pais"],
    )


def build_multi_line_chart(df: pd.DataFrame, column: str, title: str, y_title: str) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X("ano:O", title="Ano"),
            y=alt.Y(f"{column}:Q", title=y_title),
            color=alt.Color("pais:N", title="Pais"),
            tooltip=[
                alt.Tooltip("pais:N", title="Pais"),
                alt.Tooltip("ano:O", title="Ano"),
                alt.Tooltip(f"{column}:Q", title=title, format=",.2f"),
            ],
        )
        .properties(height=360, title=title)
        .interactive()
    )


def build_bar_chart(df: pd.DataFrame, x_column: str, title: str, x_title: str, color: str) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, color=color)
        .encode(
            x=alt.X(f"{x_column}:Q", title=x_title),
            y=alt.Y("pais:N", sort="-x", title="Pais"),
            tooltip=[
                alt.Tooltip("pais:N", title="Pais"),
                alt.Tooltip(f"{x_column}:Q", title=x_title, format=",.2f"),
            ],
        )
        .properties(height=280, title=title)
    )


def build_scatter_chart(df: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_circle(size=220, opacity=0.85)
        .encode(
            x=alt.X("alta_salario_pct:Q", title="Crescimento salarial no periodo (%)"),
            y=alt.Y("alta_preco_pct:Q", title="Crescimento do preco da habitacao (%)"),
            color=alt.Color("pais:N", title="Pais"),
            tooltip=[
                alt.Tooltip("pais:N", title="Pais"),
                alt.Tooltip("alta_salario_pct:Q", title="Salario", format=",.2f"),
                alt.Tooltip("alta_preco_pct:Q", title="Habitacao", format=",.2f"),
                alt.Tooltip("gap_preco_salario_pct:Q", title="Gap", format=",.2f"),
            ],
        )
        .properties(height=320, title="Preco da habitacao subiu mais que os salarios?")
    )


def build_heatmap(df: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_rect()
        .encode(
            x=alt.X("ano:O", title="Ano"),
            y=alt.Y("pais:N", title="Pais"),
            color=alt.Color(
                "preco_rendimento_ratio:Q",
                title="Relacao preco/rendimento",
                scale=alt.Scale(scheme="oranges"),
            ),
            tooltip=[
                alt.Tooltip("pais:N", title="Pais"),
                alt.Tooltip("ano:O", title="Ano"),
                alt.Tooltip("preco_rendimento_ratio:Q", title="Ratio", format=",.2f"),
            ],
        )
        .properties(height=260, title="Mapa de calor da acessibilidade habitacional")
    )


def build_pressure_chart(df: pd.DataFrame) -> alt.Chart:
    filtered = df.dropna(subset=["pressao_compra_pct"])
    return (
        alt.Chart(filtered)
        .mark_bar()
        .encode(
            x=alt.X("ano:O", title="Ano"),
            y=alt.Y("pressao_compra_pct:Q", title="Preco - salario (%)"),
            color=alt.Color(
                "pressao_compra_pct:Q",
                scale=alt.Scale(domainMid=0, scheme="redblue"),
                title="Pressao",
            ),
            column=alt.Column("pais:N", title=None),
            tooltip=[
                alt.Tooltip("pais:N", title="Pais"),
                alt.Tooltip("ano:O", title="Ano"),
                alt.Tooltip("pressao_compra_pct:Q", title="Pressao", format=",.2f"),
            ],
        )
        .properties(height=220, title="Em quais anos a habitacao pressionou mais o poder de compra?")
    )


def render_key_findings(summary: pd.DataFrame) -> None:
    top_gap = summary.iloc[0]
    best_gap = summary.iloc[-1]
    worst_ratio = summary.loc[summary["piora_ratio_pct"].idxmax()]
    worst_real_salary = summary.loc[summary["perda_salario_real_pct"].idxmax()]

    st.subheader("Leituras principais")
    st.markdown(
        f"- **{top_gap['pais']}** teve o maior descolamento entre habitacao e salario: "
        f"{top_gap['alta_preco_pct']:.1f}% vs {top_gap['alta_salario_pct']:.1f}%."
    )
    st.markdown(
        f"- **{worst_ratio['pais']}** teve a maior piora de acessibilidade: "
        f"{worst_ratio['piora_ratio_pct']:.1f}% no indicador preco/rendimento."
    )
    st.markdown(
        f"- **{worst_real_salary['pais']}** teve a maior perda no salario real estimado: "
        f"{worst_real_salary['perda_salario_real_pct']:.1f}% em relacao ao inicio do periodo."
    )
    st.markdown(
        f"- **{best_gap['pais']}** foi o pais com menor distancia entre o aumento do preco da habitacao "
        f"e o crescimento salarial dentro do recorte atual."
    )


def render_charts(filtered_df: pd.DataFrame, summary: pd.DataFrame) -> None:
    st.subheader("Painel analitico")

    col1, col2 = st.columns(2)
    with col1:
        st.altair_chart(
            build_multi_line_chart(
                filtered_df,
                "preco_rendimento_ratio",
                "Evolucao da acessibilidade habitacional",
                "Relacao preco/rendimento",
            ),
            use_container_width=True,
        )
    with col2:
        st.altair_chart(
            build_multi_line_chart(
                filtered_df,
                "indice_salario_real_base100",
                "Indice de salario real (base 100 no inicio do periodo)",
                "Indice",
            ),
            use_container_width=True,
        )

    col3, col4 = st.columns(2)
    with col3:
        st.altair_chart(
            build_bar_chart(
                summary,
                "gap_preco_salario_pct",
                "Gap entre alta da habitacao e alta salarial",
                "Gap percentual",
                "#b91c1c",
            ),
            use_container_width=True,
        )
    with col4:
        st.altair_chart(build_scatter_chart(summary), use_container_width=True)

    col5, col6 = st.columns(2)
    with col5:
        st.altair_chart(build_heatmap(filtered_df), use_container_width=True)
    with col6:
        st.altair_chart(
            build_bar_chart(
                summary,
                "perda_salario_real_pct",
                "Perda estimada de salario real no periodo",
                "Perda percentual",
                "#1d4ed8",
            ),
            use_container_width=True,
        )

    st.altair_chart(build_pressure_chart(filtered_df), use_container_width=True)


def render_table(summary: pd.DataFrame) -> None:
    st.subheader("Resumo comparativo")
    display_df = summary[
        [
            "pais",
            "alta_preco_pct",
            "alta_salario_pct",
            "gap_preco_salario_pct",
            "piora_ratio_pct",
            "perda_salario_real_pct",
            "inflacao_media",
        ]
    ].rename(
        columns={
            "pais": "Pais",
            "alta_preco_pct": "Alta habitacao (%)",
            "alta_salario_pct": "Alta salario (%)",
            "gap_preco_salario_pct": "Gap habitacao-salario (%)",
            "piora_ratio_pct": "Piora acessibilidade (%)",
            "perda_salario_real_pct": "Perda salario real (%)",
            "inflacao_media": "Inflacao media (%)",
        }
    )
    numeric_columns = [
        "Alta habitacao (%)",
        "Alta salario (%)",
        "Gap habitacao-salario (%)",
        "Piora acessibilidade (%)",
        "Perda salario real (%)",
        "Inflacao media (%)",
    ]
    st.dataframe(
        display_df.style.format({column: "{:.2f}" for column in numeric_columns}),
        use_container_width=True,
        hide_index=True,
    )


def render_suggestions() -> None:
    st.subheader("Graficos e informacoes relevantes para explicar o tema")
    st.markdown(
        "- **Gap entre habitacao e salario**: mostra se o preco dos imoveis sobe mais rapido do que a renda."
    )
    st.markdown(
        "- **Salario real ao longo do tempo**: ajuda a separar crescimento nominal de ganho real apos inflacao."
    )
    st.markdown(
        "- **Relacao preco/rendimento**: e um dos melhores indicadores de acessibilidade habitacional."
    )
    st.markdown(
        "- **Heatmap por pais e ano**: facilita enxergar em que momentos a piora ficou mais intensa."
    )
    st.markdown(
        "- **Scatter salario vs habitacao**: deixa claro quais paises ficaram mais desequilibrados."
    )
    st.markdown(
        "- **Texto de leitura principal**: destacar quem piorou mais, quem resistiu melhor e em que anos houve mais pressao."
    )


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")

    base_df = add_derived_columns(load_data(CSV_PATH))
    filtered_df, selected_countries, year_range = filter_data(base_df)

    if filtered_df.empty or not selected_countries:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
        return

    summary = build_summary_table(filtered_df)
    render_header(filtered_df, summary, year_range)
    render_key_findings(summary)
    render_charts(filtered_df, summary)
    render_table(summary)
    render_suggestions()


if __name__ == "__main__":
    main()
