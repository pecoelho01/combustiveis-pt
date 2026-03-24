import streamlit as st
import pandas as pd
import os

from components import (avgfuelprice,
                        liststationsgasoleo
                        )

st.title("Combustíveis em Portugal")
api_key = st.secrets.get("APIABERTA_API_KEY") or os.getenv("APIABERTA_API_KEY")

if not api_key:
    st.error("API key em falta. Define `APIABERTA_API_KEY` em Secrets (Streamlit Cloud) ou variável de ambiente.")
    st.stop()

choice = st.selectbox(
    "O que deseja fazer?",
    (
        "Preços médios em Portugal",
        "Postos de combustível - gasóleo"
    ),
)

if choice == "Preços médios em Portugal":

    st.markdown("Tabela com os preços médios em Portugal dos combustíveis")
    data_list, data_update = avgfuelprice(api_key=api_key)

    df_data = pd.DataFrame(data_list)
    st.dataframe(df_data, use_container_width=True)
    st.text(f"Atualizado a: {data_update} ")

if choice == "Postos de combustível - gasóleo":
    concelho = st.text_input("Concelho: (se quiseres todos escreve 'Geral')")
    concelho_filter = concelho.strip() or None
    all_stations = liststationsgasoleo(concelho_filter, api_key=api_key)
    df_data = pd.DataFrame(all_stations)
    st.dataframe(df_data, use_container_width=True)
