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

        if fuel_name == "Gasóleo de aquecimento" or fuel_name == "Gasóleo colorido" or fuel_name == "Biodiesel B15" or fuel_name == "Gasolina mistura (2 tempos)":
            continue
        else: 
            data_list.append({
                "Combustível": fuel_name,
                "Preço médio (€)": av_price
            })

    return data_list, data_update