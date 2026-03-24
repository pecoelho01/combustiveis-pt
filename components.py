import requests as rq

def avgfuelprice():
    url = "https://api.apiaberta.pt/v1/fuel/prices"
    response = rq.get(url, timeout=12)
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


def liststationsgasoleo(max_pages=25):
    all_stations = []
    page = 1
    limit_per_page = 100

    while page <= max_pages:
        url = f"https://api.apiaberta.pt/v1/fuel/stations?fuel=diesel&page={page}&limit={limit_per_page}"
        try:
            response1 = rq.get(url, timeout=12)
            response1.raise_for_status()
        except rq.RequestException:
            break

        dados1 = response1.json().get('data', [])

        if not dados1:
            break

        for item in dados1:
            station_name = item.get('name')
            marca = item.get('brand')
            fuel_name = item.get('fuel_name')
            av_price = item.get('price_eur')
            municipality = item.get('municipality')

            all_stations.append({
                'Marca': marca,
                'Bomba': station_name,
                'Concelho': municipality,
                'Combustível': fuel_name,
                'Preço (€)': av_price
            })

        page += 1

    return all_stations
