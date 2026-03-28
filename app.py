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


def render_table(df_data):
    if "Direções" in df_data.columns:
        st.dataframe(
            df_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Direções": st.column_config.LinkColumn(
                    "Direções",
                    display_text="Abrir",
                )
            },
        )
        return

    st.dataframe(df_data, use_container_width=True, hide_index=True)


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
    render_table(df_data)
