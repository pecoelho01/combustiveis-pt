import streamlit as st
import requests as rq
import pandas as pd

from components import (avgfuelprice)

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

    st.title("BREVEMENTE")