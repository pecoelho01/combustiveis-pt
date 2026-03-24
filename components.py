import requests as rq
import pandas as pd

def avgfuelprice():
    url = "https://api.apiaberta.pt/v1/fuel/prices"
    response = rq.get(url)

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


def liststationsgasoleo():
    all_stations = []
    page = 1
    limit_per_page = 100

    while True:
        url= f"https://api.apiaberta.pt/v1/fuel/stations?fuel=dieselpage={page}&limit={limit_per_page}"
        response1 = rq.get(url)
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

        page +=1

    return all_stations