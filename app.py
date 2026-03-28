import streamlit as st
import pandas as pd

from components import (avgfuelprice,
                        liststationsgasoleo
                        )

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

st.title("Combustíveis em Portugal")

choice = st.selectbox(
    "O que deseja fazer?",
    (
        "Preços médios em Portugal",
        "Postos de combustível - gasóleo"
    ),
)

if choice == "Preços médios em Portugal":

    st.markdown("Tabela com os preços médios em Portugal dos combustíveis")
    data_list, data_update = avgfuelprice()

    df_data = pd.DataFrame(data_list)
    st.dataframe(df_data, use_container_width=True)
    st.text(f"Atualizado a: {data_update} ")

if choice == "Postos de combustível - gasóleo":
    concelho = st.text_input("Concelho: (se quiseres todos escreve 'Geral')")
    concelho_filter = (concelho or "").strip()
    if not concelho_filter or concelho_filter.casefold() == "geral":
        concelho_filter = None

    all_stations = liststationsgasoleo(concelho_filter)
    df_data = pd.DataFrame(all_stations)
    st.dataframe(df_data, use_container_width=True)
