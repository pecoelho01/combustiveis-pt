import time
import threading
import requests as rq
# Ferramentas para executar pedidos HTTP em paralelo.
from concurrent.futures import ThreadPoolExecutor, as_completed

_THREAD_LOCAL = threading.local()


def _get_session():
    session = getattr(_THREAD_LOCAL, "session", None)
    if session is None:
        session = rq.Session()
        adapter = rq.adapters.HTTPAdapter(pool_connections=32, pool_maxsize=32, max_retries=0)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        _THREAD_LOCAL.session = session
    return session


def avgfuelprice():
    url = "https://api.apiaberta.pt/v1/fuel/prices"
    response = _get_session().get(url, timeout=12)
    response.raise_for_status()

    dados = response.json().get('data', [])

    data_list = []
    data_update = None

    for item in dados:
    
        fuel_name = item.get('fuel_name')
        av_price = item.get('avg_price_eur')
        data_update = item.get('date')
        
        fuel_exceptions = {"Gasóleo de aquecimento", "Gasóleo colorido", "Biodiesel B15", "Gasolina mistura (2 tempos)"}

        if fuel_name in fuel_exceptions:
            continue

        else: 
            data_list.append({
                "Combustível": fuel_name,
                "Preço médio (€)": av_price
            })

    return data_list, data_update


def _fetch_stations_page(fuel_slug, page, limit_per_page, retries=2, retry_delay=0.4):
    # Obtém uma página da API para um combustível e tenta novamente em falhas transitórias.
    url = f"https://api.apiaberta.pt/v1/fuel/stations?fuel={fuel_slug}&page={page}&limit={limit_per_page}"
    last_error = None

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


def _build_station_row(item, count):
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

    return {
        'Posto nº': count,
        'Marca': marca,
        'Bomba': station_name,
        'Concelho': municipality,
        'Combustível': fuel_name,
        'Preço (€)': av_price,
        'Direções': directions_url
    }


def liststationsbyfuel(fuel_slug, max_pages=31, max_workers=8):
    all_stations = []
    limit_per_page = 100
    count = 0
    # Guarda resultados indexados pelo número da página.
    page_results = {}
    # Evita workers inválidos e não cria mais threads do que páginas.
    worker_count = max(1, min(max_workers, max_pages))

    # Lança pedidos de várias páginas em paralelo.
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = {
            executor.submit(_fetch_stations_page, fuel_slug, page, limit_per_page): page
            for page in range(1, max_pages + 1)
        }

        # Recolhe resultados conforme forem terminando.
        for future in as_completed(futures):
            page = futures[future]
            try:
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
        dados1 = page_results.get(page)

        # Não interrompe a recolha por falha ou página vazia intermédia.
        if not dados1:
            continue

        for item in dados1:
            count = count + 1
            all_stations.append(_build_station_row(item, count))

    return all_stations


def liststationsgasoleo(max_pages=31, max_workers=8):
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
