import streamlit as st
import pandas as pd

from components import (avgfuelprice,
                        liststationsgasoleo,
                        liststationsgasolina95,
                        liststationsgasolinaespecial95,
                        liststationsgasolina98,
                        liststationsgasolinaespecial98,
                        liststationsgasolinamistura2tempos,
                        )

FUEL_FETCHERS = {
    "Gasóleo simples": liststationsgasoleo,
    "Gasolina simples 95": liststationsgasolina95,
    "Gasolina especial 95": liststationsgasolinaespecial95,
    "Gasolina 98": liststationsgasolina98,
    "Gasolina especial 98": liststationsgasolinaespecial98,
    "Gasolina mistura (2 tempos)": liststationsgasolinamistura2tempos,
}

st.set_page_config(
    page_title="Combustíveis em Portugal",
    layout="wide",
)

st.markdown(
    """
    <style>
        .main .block-container {
            max-width: 1200px;
            padding-top: 1.5rem;
            padding-bottom: 1.5rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 1.6rem;
                line-height: 1.25;
            }

            .main .block-container {
                padding-top: 1rem;
                padding-left: 0.75rem;
                padding-right: 0.75rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=300)
def get_avg_prices_cached():
    return avgfuelprice()


@st.cache_data(ttl=300)
def get_stations_cached(fuel_label):
    fetch_fn = FUEL_FETCHERS[fuel_label]
    return fetch_fn()


def render_table(df_data, allow_html=False):
    if df_data.empty:
        st.dataframe(df_data, use_container_width=True)
        return

    table_html = df_data.to_html(index=False, escape=not allow_html)
    st.markdown(f'<div style="overflow-x:auto;">{table_html}</div>', unsafe_allow_html=True)


st.title("Combustíveis em Portugal")

choice = st.selectbox(
    "O que deseja fazer?",
    (
        "Preços médios em Portugal",
        "Postos de combustível"
    ),
)

if choice == "Preços médios em Portugal":

    st.markdown("Tabela com os preços médios em Portugal dos combustíveis")
    data_list, data_update = get_avg_prices_cached()
    df_data = pd.DataFrame(data_list)
    render_table(df_data)
    st.text(f"Atualizado a: {data_update} ")

if choice == "Postos de combustível":
    fuel_label = st.selectbox(
        "Combustível",
        tuple(FUEL_FETCHERS.keys()),
        index=0,
    )
    df_data = pd.DataFrame(get_stations_cached(fuel_label))
    if not df_data.empty and "Direções" in df_data.columns:
        df_data["Direções"] = df_data["Direções"].apply(
            lambda url: f'<a href="{url}" target="_blank" rel="noopener noreferrer">Abrir</a>' if url else ""
        )
        render_table(df_data, allow_html=True)
    else:
        render_table(df_data)
