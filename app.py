import streamlit as st
import pandas as pd

from components import (avgfuelprice,
                        liststationsgasoleo
                        )

INITIAL_PAGES = 5
PAGE_STEP = 5
MAX_PAGES = 25


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
def get_stations_cached(max_pages):
    return liststationsgasoleo(max_pages=max_pages)


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
    if "stations_pages" not in st.session_state:
        st.session_state.stations_pages = INITIAL_PAGES

    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.caption(f"A mostrar dados até {st.session_state.stations_pages} páginas.")
    with col_b:
        if st.button(
            "Carregar mais",
            use_container_width=True,
            disabled=st.session_state.stations_pages >= MAX_PAGES,
        ):
            st.session_state.stations_pages = min(
                st.session_state.stations_pages + PAGE_STEP,
                MAX_PAGES,
            )

    df_data = get_stations_cached(max_pages=st.session_state.stations_pages)
    st.dataframe(df_data, use_container_width=True)
