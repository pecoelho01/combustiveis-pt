import threading
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Bibliotecas da interface e mapa.
import folium
import pandas as pd
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# Funções que vão buscar dados à API.
from components import (
    avgfuelprice,
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

# Configuração geral da página Streamlit.
st.set_page_config(page_title="Combustíveis em Portugal", layout="wide")

# CSS para melhorar layout em PC e telemóvel.
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


def get_week_key():
    """Devolve a data da segunda-feira da semana atual (fuso Europe/Lisbon)."""
    # Hoje, no fuso de Lisboa.
    today = datetime.now(ZoneInfo("Europe/Lisbon")).date()
    # weekday(): segunda=0 ... domingo=6
    monday = today - timedelta(days=today.weekday())
    # Exemplo: "2026-03-30"
    return monday.isoformat()


# Chave semanal para invalidar cache automaticamente na mudança de semana.
WEEK_KEY = get_week_key()
# Guarda semanas que já iniciaram o prewarm (evita arrancar várias vezes).
PREWARM_STARTED = set()


@st.cache_data(show_spinner=False, max_entries=20)
def get_avg_prices_cached(week_key):
    # A função depende da semana (argumento usado apenas para chave de cache).
    _ = week_key
    return avgfuelprice()


@st.cache_data(show_spinner=False, max_entries=20)
def get_stations_cached(fuel_label, week_key):
    # Cache por combustível + semana.
    _ = week_key
    return FUEL_FETCHERS[fuel_label]()


def start_weekly_prewarm(week_key):
    """Aquece o cache da semana em background para evitar esperas aos utilizadores."""
    # Se já foi iniciado nesta semana, não volta a arrancar.
    if week_key in PREWARM_STARTED:
        return

    PREWARM_STARTED.add(week_key)

    def warm_cache():
        # Pré-carrega preços médios.
        get_avg_prices_cached(week_key)
        # Pré-carrega postos para todos os combustíveis.
        for label in FUEL_FETCHERS:
            get_stations_cached(label, week_key)

    # Background thread para não bloquear o carregamento da página.
    threading.Thread(target=warm_cache, daemon=True).start()


def render_table(df_data):
    # Se a coluna Direções existir, mostra como link clicável.
    if "Direções" in df_data.columns:
        st.dataframe(
            df_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Direções": st.column_config.LinkColumn("Direções", display_text="Abrir")
            },
        )
        return

    # Caso normal: tabela simples.
    st.dataframe(df_data, use_container_width=True, hide_index=True)


st.title("Combustíveis em Portugal")
# Arranca o prewarm assim que alguém abre a app.
start_weekly_prewarm(WEEK_KEY)

# Menu principal da app.
choice = st.selectbox(
    "O que deseja fazer?",
    ("Preços médios em Portugal", "Postos de combustível"),
)

if choice == "Preços médios em Portugal":
    # Busca dados de preços médios a partir do cache semanal.
    st.markdown("Tabela com os preços médios em Portugal dos combustíveis")
    data_list, data_update = get_avg_prices_cached(WEEK_KEY)
    df_data = pd.DataFrame(data_list)
    render_table(df_data)
    st.text(f"Atualizado a: {data_update}")

if choice == "Postos de combustível":
    # Escolha do combustível para listar postos.
    fuel_label = st.selectbox("Combustível", tuple(FUEL_FETCHERS.keys()), index=0)

    # Spinner visível enquanto os dados carregam.
    with st.spinner("A carregar postos..."):
        df_data = pd.DataFrame(get_stations_cached(fuel_label, WEEK_KEY))

    # Não mostramos Latitude/Longitude na tabela final.
    df_table = df_data.drop(columns=["Latitude", "Longitude"], errors="ignore")
    render_table(df_table)

    # Para o mapa, ficam apenas linhas com coordenadas válidas.
    df_map = df_data.dropna(subset=["Latitude", "Longitude"]).copy()
    st.caption(f"A mostrar {len(df_map)} postos no mapa.")

    # Só desenha mapa quando há pontos.
    if not df_map.empty:
        # Centro inicial = média das coordenadas.
        center_lat = df_map["Latitude"].mean()
        center_lon = df_map["Longitude"].mean()

        # Mapa base.
        m = folium.Map(location=[center_lat, center_lon], zoom_start=7, prefer_canvas=True)
        # Cluster junta pontos próximos para evitar sobreposição visual.
        marker_cluster = MarkerCluster(
            chunkedLoading=True,
            chunkInterval=100,
            chunkDelay=25,
        ).add_to(m)

        # Um marcador por posto.
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
                # Tooltip aparece ao passar o rato.
                tooltip=row.get("Bomba", "Posto"),
            ).add_to(marker_cluster)

        st.subheader("Mapa dos postos")
        # Render do mapa Folium dentro do Streamlit.
        st_folium(m, use_container_width=True, height=520)
