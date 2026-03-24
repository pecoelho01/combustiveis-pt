import streamlit as st
import pandas as pd

from components import (avgfuelprice,
                        liststationsgasoleo
                        )

st.set_page_config(page_title="Combustíveis em Portugal", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(1200px 500px at 5% -10%, #e6f0ff 10%, transparent 60%),
            radial-gradient(1000px 500px at 100% 0%, #fff1dc 10%, transparent 55%),
            #f8fafc;
    }
    .title-band {
        background: linear-gradient(90deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        color: #ffffff;
        padding: 16px 20px;
        border-radius: 14px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.2);
        margin-bottom: 14px;
    }
    .title-band h1 {
        margin: 0;
        font-size: 1.7rem;
        letter-spacing: .2px;
    }
    .soft-card {
        background: #ffffff;
        border: 1px solid #dbe2ea;
        border-radius: 12px;
        padding: 12px 14px;
        margin: 8px 0 12px 0;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.06);
    }
    .updated-pill {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        background: #e2e8f0;
        color: #0f172a;
        font-size: 0.85rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="title-band">
      <h1>Combustíveis em Portugal</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(ttl=1800)
def get_avgfuelprice_data():
    return avgfuelprice()


@st.cache_data(ttl=1800)
def get_gasoleo_stations_data():
    return liststationsgasoleo(max_pages=25)


choice = st.selectbox(
    "O que deseja fazer?",
    (
        "Preços médios em Portugal",
        "Postos de combustível - gasóleo"
    ),
)

if choice == "Preços médios em Portugal":

    st.markdown(
        '<div class="soft-card">Tabela com os preços médios em Portugal dos combustíveis.</div>',
        unsafe_allow_html=True
    )
    data_list, data_update = get_avgfuelprice_data()

    df_data = pd.DataFrame(data_list)
    if not df_data.empty:
        df_data["Preço médio (€)"] = pd.to_numeric(df_data["Preço médio (€)"], errors="coerce")
        df_data = df_data.sort_values(by="Preço médio (€)", ascending=True)
        st.dataframe(
            df_data,
            use_container_width=True,
            height=470,
            hide_index=True,
            column_config={
                "Preço médio (€)": st.column_config.NumberColumn(format="%.3f €")
            }
        )
    else:
        st.warning("Sem dados para apresentar no momento.")

    st.markdown(f'<span class="updated-pill">Atualizado a: {data_update}</span>', unsafe_allow_html=True)

if choice == "Postos de combustível - gasóleo":

    with st.spinner("A carregar postos de combustível..."):
        all_stations = get_gasoleo_stations_data()
    df_data = pd.DataFrame(all_stations)
    if not df_data.empty:
        df_data["Preço (€)"] = pd.to_numeric(df_data["Preço (€)"], errors="coerce")
        df_data = df_data.sort_values(by="Preço (€)", ascending=True)
        st.dataframe(
            df_data,
            use_container_width=True,
            height=520,
            hide_index=True,
            column_config={
                "Preço (€)": st.column_config.NumberColumn(format="%.3f €")
            }
        )
        st.caption(f"{len(df_data)} postos carregados (cache 30 min).")
    else:
        st.warning("Sem dados para apresentar no momento. Tenta atualizar a página.")
