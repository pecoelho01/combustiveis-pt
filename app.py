import streamlit as st
import requests as rq
import pandas as pd
import time

st.title("Combustíveis em Portugal")

st.markdown("Tabela com os preços médios em Portugal dos combustíveis")

url = "https://api.apiaberta.pt/v1/fuel/prices"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


def is_html_body(text):
    snippet = (text or "").lstrip().lower()
    return snippet.startswith("<!doctype html") or "<html" in snippet[:200]


def show_technical_details(status_code, content_type, body):
    with st.expander("Detalhes técnicos"):
        st.write(f"HTTP {status_code}")
        st.write(f"Content-Type: {content_type or 'desconhecido'}")
        if not body:
            st.caption("Sem corpo na resposta.")
        elif is_html_body(body):
            st.caption("Corpo HTML omitido (página de erro do gateway/proxy).")
        else:
            st.code(body[:500])

MAX_RETRIES = 3
RETRY_HTTP_CODES = {502, 503, 504}
response = None
last_exception = None

for attempt in range(1, MAX_RETRIES + 1):
    try:
        response = rq.get(url, headers=headers, timeout=20)
        if response.status_code in RETRY_HTTP_CODES and attempt < MAX_RETRIES:
            time.sleep(attempt)
            continue
        break
    except rq.exceptions.RequestException as exc:
        last_exception = exc
        if attempt < MAX_RETRIES:
            time.sleep(attempt)
            continue

if response is None:
    st.error(f"Erro ao contactar a API após {MAX_RETRIES} tentativas: {last_exception}")
    st.stop()

if response.status_code != 200:
    if response.status_code in RETRY_HTTP_CODES:
        st.error(
            f"A API está temporariamente indisponível (HTTP {response.status_code}). "
            "Tenta novamente dentro de alguns minutos."
        )
    else:
        st.error(f"A API devolveu HTTP {response.status_code}")
    show_technical_details(
        status_code=response.status_code,
        content_type=response.headers.get("Content-Type", ""),
        body=response.text,
    )
    st.stop()

content_type = response.headers.get("Content-Type", "").lower()
if "application/json" not in content_type:
    st.error(f"A API não devolveu JSON (Content-Type: {content_type or 'desconhecido'})")
    show_technical_details(
        status_code=response.status_code,
        content_type=content_type,
        body=response.text,
    )
    st.stop()

try:
    payload = response.json()
except ValueError:
    st.error("A API devolveu um corpo inválido para JSON.")
    show_technical_details(
        status_code=response.status_code,
        content_type=content_type,
        body=response.text,
    )
    st.stop()

dados = payload.get("data", [])
if not isinstance(dados, list):
    st.error("Formato inesperado: o campo 'data' não é uma lista.")
    st.stop()
data_list = []

for item in dados:
  fuel_name = item.get('fuel_name')
  av_price = item.get('avg_price_eur')

  data_list.append({
    "Combustível": fuel_name,
    "Preço médio": av_price
  })

df_data = pd.DataFrame(data_list)
st.dataframe(df_data, use_container_width=True)
