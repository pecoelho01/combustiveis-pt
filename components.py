import os
import math
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
    load_dotenv()

_THREAD_LOCAL = threading.local()
_API_KEY = os.getenv("APIABERTA_API_KEY", "").strip()


def _get_env_int(name, default):
    try:
        value = int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


_REQUEST_TIMEOUT_SECONDS = _get_env_int("APIABERTA_TIMEOUT_SECONDS", 8)
_STATIONS_PAGE_LIMIT = _get_env_int("APIABERTA_STATIONS_PAGE_LIMIT", 100)
_STATIONS_MAX_PAGES = _get_env_int("APIABERTA_STATIONS_MAX_PAGES", 60)
_STATIONS_MAX_WORKERS = _get_env_int("APIABERTA_STATIONS_MAX_WORKERS", 12)


def _get_session():
    session = getattr(_THREAD_LOCAL, "session", None)
    if session is None:
        session = rq.Session()
        adapter = rq.adapters.HTTPAdapter(pool_connections=32, pool_maxsize=32, max_retries=0)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        if _API_KEY:
            session.headers.update({"X-API-Key": _API_KEY})
        _THREAD_LOCAL.session = session
    return session


def avgfuelprice():
    url = "https://api.apiaberta.pt/v1/fuel/prices"
    response = _get_session().get(url, timeout=_REQUEST_TIMEOUT_SECONDS)
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


def _to_positive_int(value):
    try:
        int_value = int(value)
    except (TypeError, ValueError):
        return None
    return int_value if int_value > 0 else None


def _extract_total_pages(payload, limit_per_page):
    if not isinstance(payload, dict):
        return None

    candidate_dicts = [
        payload,
        payload.get("meta"),
        payload.get("pagination"),
        payload.get("page_info"),
        payload.get("pageInfo"),
    ]

    for candidate in candidate_dicts:
        if not isinstance(candidate, dict):
            continue

        for key in ("total_pages", "totalPages", "last_page", "lastPage", "pages", "pageCount", "page_count"):
            value = _to_positive_int(candidate.get(key))
            if value is not None:
                return value

        for key in ("total", "total_items", "totalItems", "count", "station_count", "stationCount"):
            total_items = _to_positive_int(candidate.get(key))
            if total_items is not None and limit_per_page > 0:
                return max(1, math.ceil(total_items / limit_per_page))

    return None


def _fetch_stations_page(
    fuel_slug,
    page,
    limit_per_page,
    retries=1,
    retry_delay=0.35,
    timeout=_REQUEST_TIMEOUT_SECONDS,
):
    # Obtém uma página da API para um combustível e tenta novamente em falhas transitórias.
    url = "https://api.apiaberta.pt/v1/fuel/stations"
    params = {"fuel": fuel_slug, "page": page, "limit": limit_per_page}
    last_error = None

    for attempt in range(retries + 1):
        try:
            response = _get_session().get(url, params=params, timeout=timeout)
            response.raise_for_status()
            payload = response.json()
            return page, payload.get("data", []), payload
        except rq.HTTPError as exc:
            last_error = exc
            status_code = exc.response.status_code if exc.response is not None else None

            if status_code in {400, 401, 403, 404}:
                break

            if status_code == 429 and attempt < retries:
                retry_after = exc.response.headers.get("Retry-After") if exc.response is not None else None
                retry_after_seconds = _to_positive_int(retry_after)
                sleep_seconds = retry_after_seconds if retry_after_seconds is not None else retry_delay * (attempt + 1)
                time.sleep(min(max(sleep_seconds, 0.2), 5))
                continue

            if attempt < retries:
                time.sleep(retry_delay * (attempt + 1))
        except (rq.RequestException, ValueError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(retry_delay * (attempt + 1))

    raise last_error


def _fetch_pages_parallel(fuel_slug, pages, limit_per_page, max_workers):
    page_results = {}
    if not pages:
        return page_results

    worker_count = max(1, min(max_workers, len(pages)))
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = {
            executor.submit(_fetch_stations_page, fuel_slug, page, limit_per_page): page
            for page in pages
        }

        for future in as_completed(futures):
            page = futures[future]
            try:
                _, data, _ = future.result()
            except rq.RequestException:
                page_results[page] = None
            except Exception:
                page_results[page] = None
            else:
                page_results[page] = data

    return page_results


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
        'Direções': directions_url,
        "Latitude": lat,
        "Longitude": lng
    }


def liststationsbyfuel(fuel_slug, max_pages=None, max_workers=None):
    all_stations = []
    limit_per_page = _STATIONS_PAGE_LIMIT
    count = 0
    page_results = {}

    max_pages = max(1, max_pages if max_pages is not None else _STATIONS_MAX_PAGES)
    max_workers = max(1, max_workers if max_workers is not None else _STATIONS_MAX_WORKERS)

    # Página 1 primeiro para detetar paginação real e evitar pedidos desnecessários.
    try:
        _, first_page_data, first_payload = _fetch_stations_page(fuel_slug, 1, limit_per_page)
    except rq.RequestException:
        return all_stations
    except Exception:
        return all_stations

    if not first_page_data:
        return all_stations

    page_results[1] = first_page_data

    total_pages = _extract_total_pages(first_payload, limit_per_page)
    if total_pages is not None:
        max_pages = min(max_pages, total_pages)

    if max_pages > 1:
        if total_pages is not None:
            # Com total de páginas conhecido, faz apenas os pedidos necessários.
            pages_to_fetch = list(range(2, max_pages + 1))
            page_results.update(
                _fetch_pages_parallel(fuel_slug, pages_to_fetch, limit_per_page, max_workers)
            )
        else:
            # Sem metadata de paginação, procura páginas em blocos e pára ao encontrar página vazia.
            next_page = 2
            probe_size = max(1, max_workers)

            while next_page <= max_pages:
                probe_pages = list(range(next_page, min(next_page + probe_size, max_pages + 1)))
                probe_results = _fetch_pages_parallel(
                    fuel_slug,
                    probe_pages,
                    limit_per_page,
                    max_workers,
                )

                saw_empty_page = False
                for page in sorted(probe_results.keys()):
                    dados = probe_results[page]
                    if dados is None:
                        continue
                    if not dados:
                        saw_empty_page = True
                        break
                    page_results[page] = dados

                if saw_empty_page:
                    break

                next_page = probe_pages[-1] + 1

    for page in sorted(page_results.keys()):
        dados = page_results[page]
        if not dados:
            continue

        for item in dados:
            count = count + 1
            all_stations.append(_build_station_row(item, count))

    return all_stations


def liststationsgasoleo(max_pages=None, max_workers=None):
    return liststationsbyfuel("diesel", max_pages=max_pages, max_workers=max_workers)


def liststationsgasolina95(max_pages=None, max_workers=None):
    return liststationsbyfuel("gasoline_95", max_pages=max_pages, max_workers=max_workers)


def liststationsgasolinaespecial95(max_pages=None, max_workers=None):
    return liststationsbyfuel("gasoline_95_plus", max_pages=max_pages, max_workers=max_workers)


def liststationsgasolina98(max_pages=None, max_workers=None):
    return liststationsbyfuel("gasoline_98", max_pages=max_pages, max_workers=max_workers)


def liststationsgasolinaespecial98(max_pages=None, max_workers=None):
    return liststationsbyfuel("gasoline_98_plus", max_pages=max_pages, max_workers=max_workers)


def liststationsgasolinamistura2tempos(max_pages=None, max_workers=None):
    return liststationsbyfuel("gasoline_2stroke", max_pages=max_pages, max_workers=max_workers)
