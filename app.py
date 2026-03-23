import streamlit as st
import requests as rq
import pandas as pd

st.title("Combustíveis em Portugal")

st.markdown("Tabela com os preços médios em Portugal dos combustíveis")

url = "https://api.apiaberta.pt/v1/fuel/prices"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}
response = rq.get(url, headers=headers)
print(response.text) #Debug 

dados = response.json().get('data', [])

data_list = []

for item in dados:
  fuel_name = item['fuel_name']
  av_price = item['avg_price_eur']

  data_list.append({
    "Combustível": fuel_name,
    "Preço médio": av_price
  })

df_data = pd.DataFrame(data_list)
st.dataframe(df_data, use_container_width=True)

