import os
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium


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


def _get_env_int(name, default):
    try:
        value = int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


_AVG_CACHE_TTL_SECONDS = _get_env_int("AVG_PRICES_CACHE_TTL_SECONDS", 900)
_STATIONS_CACHE_TTL_SECONDS = _get_env_int("STATIONS_CACHE_TTL_SECONDS", 3600)


@st.cache_data(ttl=_AVG_CACHE_TTL_SECONDS, show_spinner=False)
def get_avg_prices_cached():
    return avgfuelprice()


@st.cache_data(ttl=_STATIONS_CACHE_TTL_SECONDS, show_spinner=False)
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
    with st.spinner("A carregar postos..."):
        df_data = pd.DataFrame(get_stations_cached(fuel_label))
    df_table = df_data.drop(columns=["Latitude", "Longitude"], errors="ignore")
    render_table(df_table)

    # Dá só as linhas com coordenadas válidas.
    df_map = df_data.dropna(subset=["Latitude", "Longitude"]).copy()
    total_points = len(df_map)
    st.caption(f"A mostrar {total_points} postos no mapa.")

    # Só constrói o mapa se existirem pontos válidos.
    if not df_map.empty:
        # Centro do mapa vai ser a média das coordenadas, lat e long
        center_lat = df_map["Latitude"].mean()
        center_lon = df_map["Longitude"].mean()

        # Cria o mapa base.
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            prefer_canvas=True,
        )
        marker_cluster = MarkerCluster(
            chunkedLoading=True,
            chunkInterval=100,
            chunkDelay=25,
        ).add_to(m)

        # Cria um pop-up por bomba de combustível.
        for row in df_map.to_dict("records"):
            popup_html = f"""
            <b>{row.get('Bomba', '')}</b><br>
            Marca: {row.get('Marca', '')}<br>
            Concelho: {row.get('Concelho', '')}<br>
            Preço: {row.get('Preço (€)', '')} €<br>
            <a href="{row.get('Direções', '')}" target="_blank">Abrir direções</a>
            """
            folium.Marker(
                location=[row.get("Latitude"), row.get("Longitude")],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=row.get("Bomba", "Posto"),
            ).add_to(marker_cluster)

        st.subheader("Mapa dos postos")
        try:
            st_folium(
                m,
                use_container_width=True,
                height=520,
                returned_objects=[],
            )
        except TypeError:
            # Compatibilidade com versões antigas de streamlit-folium.
            st_folium(m, use_container_width=True, height=520)
