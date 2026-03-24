import streamlit as st
import pandas as pd
import os

from components import (avgfuelprice,
                        liststationsgasoleo
                        )

st.title("Combustíveis em Portugal")
api_key = st.secrets.get("APIABERTA_API_KEY") or os.getenv("APIABERTA_API_KEY")

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

    all_stations = liststationsgasoleo(api_key=api_key)
    df_data = pd.DataFrame(all_stations)
    st.dataframe(df_data, use_container_width=True)
