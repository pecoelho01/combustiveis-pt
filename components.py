import os
import time
import threading
import requests as rq
# Ferramentas para executar pedidos HTTP em paralelo.
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv is not None:
    # Carrega variáveis definidas no ficheiro .env (se existir).
    load_dotenv()

# Armazena uma sessão HTTP por thread.
_THREAD_LOCAL = threading.local()
# API key opcional para enviar no header X-API-Key.
_API_KEY = os.getenv("APIABERTA_API_KEY", "").strip()


def _get_session():
    # Reutilizar Session melhora performance (ligações keep-alive).
    session = getattr(_THREAD_LOCAL, "session", None)
    if session is None:
        session = rq.Session()
        # Adapter com pool de ligações para várias requests.
        adapter = rq.adapters.HTTPAdapter(pool_connections=32, pool_maxsize=32, max_retries=0)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        # Se existir API key, aplica na sessão inteira.
        if _API_KEY:
            session.headers.update({"X-API-Key": _API_KEY})
        _THREAD_LOCAL.session = session
    return session


def avgfuelprice():
    # Endpoint de preços médios.
    url = "https://api.apiaberta.pt/v1/fuel/prices"
    response = _get_session().get(url, timeout=12)
    response.raise_for_status()

    dados = response.json().get('data', [])

    data_list = []
    data_update = None

    for item in dados:
        # Campos que vamos usar da API.
        fuel_name = item.get('fuel_name')
        av_price = item.get('avg_price_eur')
        data_update = item.get('date')

        fuel_exceptions = {
            "Gasóleo de aquecimento",
            "Gasóleo colorido",
            "Biodiesel B15",
            "Gasolina mistura (2 tempos)",
        }

        if fuel_name in fuel_exceptions:
            continue

        # Formato final da linha para mostrar na tabela.
        data_list.append({
            "Combustível": fuel_name,
            "Preço médio (€)": av_price
        })

    return data_list, data_update


def fetch_stations_page(fuel_slug, page, limit_per_page, retries=2, retry_delay=0.4):
    # Obtém uma página da API para um combustível e tenta novamente em falhas transitórias.
    url = f"https://api.apiaberta.pt/v1/fuel/stations?fuel={fuel_slug}&page={page}&limit={limit_per_page}"
    last_error = None

    # Faz retries simples para reduzir falhas momentâneas.
    for attempt in range(retries + 1):
        try:
            response = _get_session().get(url, timeout=12)
            response.raise_for_status()
            return page, response.json().get('data', [])
        except rq.RequestException as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(retry_delay * (attempt + 1))

    raise last_error


def build_station_row(item, count):
    # Campos principais recebidos da API.
    station_name = item.get('name')
    marca = item.get('brand')
    fuel_name = item.get('fuel_name')
    av_price = item.get('price_eur')
    municipality = item.get('municipality')
    lat = item.get("location", {}).get("lat")
    lng = item.get("location", {}).get("lng")

    directions_url = ""
    if lat is not None and lng is not None:
        directions_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"

    # Estrutura final usada pelo app.py (tabela + mapa).
    return {
        'Posto nº': count,
        'Marca': marca,
        'Bomba': station_name,
        'Concelho': municipality,
        'Combustível': fuel_name,
        'Preço (€)': av_price,
        'Direções': directions_url,
        'Latitude': lat,
        'Longitude': lng,
    }


def liststationsbyfuel(fuel_slug, max_pages=31, max_workers=8):
    # Lista final com todos os postos encontrados.
    all_stations = []
    # Quantos resultados por página da API.
    limit_per_page = 100
    count = 0
    # Guarda resultados indexados pelo número da página.
    page_results = {}
    # Evita workers inválidos e não cria mais threads do que páginas.
    worker_count = max(1, min(max_workers, max_pages))

    # Lança pedidos de várias páginas em paralelo.
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = {
            executor.submit(fetch_stations_page, fuel_slug, page, limit_per_page): page
            for page in range(1, max_pages + 1)
        }

        # Recolhe resultados conforme forem terminando.
        for future in as_completed(futures):
            page = futures[future]
            try:
                # Cada future devolve: (número_página, dados_da_página)
                _, dados = future.result()
            except rq.RequestException:
                # Marca falha nesta página.
                page_results[page] = None
            except Exception:
                # Evita interromper o processo por erro inesperado.
                page_results[page] = None
            else:
                page_results[page] = dados

    # Reconstrói a ordem das páginas para manter sequência consistente.
    for page in range(1, max_pages + 1):
        dados = page_results.get(page)

        # Não interrompe a recolha por falha ou página vazia intermédia.
        if not dados:
            continue

        for item in dados:
            # Numeração sequencial dos postos.
            count = count + 1
            all_stations.append(build_station_row(item, count))

    return all_stations


def liststationsgasoleo(max_pages=31, max_workers=8):
    # Wrapper por tipo de combustível.
    return liststationsbyfuel("diesel", max_pages=max_pages, max_workers=max_workers)


def liststationsgasolina95(max_pages=31, max_workers=8):
    return liststationsbyfuel("gasoline_95", max_pages=max_pages, max_workers=max_workers)


def liststationsgasolinaespecial95(max_pages=31, max_workers=8):
    return liststationsbyfuel("gasoline_95_plus", max_pages=max_pages, max_workers=max_workers)


def liststationsgasolina98(max_pages=31, max_workers=8):
    return liststationsbyfuel("gasoline_98", max_pages=max_pages, max_workers=max_workers)


def liststationsgasolinaespecial98(max_pages=31, max_workers=8):
    return liststationsbyfuel("gasoline_98_plus", max_pages=max_pages, max_workers=max_workers)


def liststationsgasolinamistura2tempos(max_pages=31, max_workers=8):
    return liststationsbyfuel("gasoline_2stroke", max_pages=max_pages, max_workers=max_workers)
