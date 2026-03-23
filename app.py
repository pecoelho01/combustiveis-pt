import streamlit as st
import requests as rq
import pandas as pd

st.title("Combustíveis em Portugal")

st.markdown("Tabela com os preços médios em Portugal dos combustíveis")

url = "https://api.apiaberta.pt/v1/fuel/prices"
response = rq.get(url)

dados = response.json().get('data', [])

data_list = []

for item in dados:
  fuel_name = item.get('fuel_name')
  av_price = item.get('avg_price_eur')

  data_list.append({
    "Combustível": fuel_name,
    "Preço médio": av_price
  })

df_data = pd.DataFrame(data_list)
st.dataframe(df_data, use_container_width=False)
