# Combustiveis PT

## PT

Aplicação em Streamlit para consultar preços médios e postos de combustível em Portugal, com dados da API Aberta.

Demo online: [https://combustiveis-pt.streamlit.app/](https://combustiveis-pt.streamlit.app/)

### Funcionalidades
- Mostrar preços médios de combustíveis em Portugal.
- Mostrar data da última atualização dos preços médios.
- Listar postos por tipo de combustível:
  - Gasóleo simples
  - Gasolina simples 95
  - Gasolina especial 95
  - Gasolina 98
  - Gasolina especial 98
  - Gasolina mistura (2 tempos)
- Mostrar link de direções por posto (`Direções -> Abrir`) para Google Maps.
- Interface responsiva para desktop e mobile.

### Stack
- Python
- Streamlit
- Pandas
- Requests

### Performance
- Cache configurável por variável de ambiente (por omissão: 15 min para preços médios e 60 min para listagens de postos).
- Recolha de páginas em paralelo (`ThreadPoolExecutor`) com paginação dinâmica para reduzir pedidos desnecessários.
- Reutilização de ligações HTTP com `requests.Session()`.
- Retry automático em falhas transitórias de rede/API.
- Renderização de mapa com clustering para melhor legibilidade com muitos postos.

### Como correr localmente
1. Clonar o repositório:
   ```bash
   git clone https://github.com/<your-user>/combustiveis-pt.git
   cd combustiveis-pt
   ```
2. (Opcional) Criar e ativar ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Instalar dependências:
   ```bash
   pip install streamlit pandas requests python-dotenv
   ```
4. Criar o ficheiro `.env` com a API key:
   ```bash
   cp .env.example .env
   ```
   Depois editar o `.env` e definir:
   ```bash
   APIABERTA_API_KEY=<SUA_API_KEY>
   ```
   (Opcional) Afinar performance no `.env`:
   ```bash
   AVG_PRICES_CACHE_TTL_SECONDS=900
   STATIONS_CACHE_TTL_SECONDS=3600
   APIABERTA_STATIONS_MAX_WORKERS=12
   APIABERTA_STATIONS_MAX_PAGES=60
   ```
5. Executar a aplicação:
   ```bash
   streamlit run app.py
   ```

### Estrutura
- `app.py`: interface principal da aplicação.
- `components.py`: funções de recolha/processamento de preços e postos por combustível.

---

## EN

Streamlit app to check average fuel prices and fuel stations in Portugal using data from API Aberta.

Live demo: [https://combustiveis-pt.streamlit.app/](https://combustiveis-pt.streamlit.app/)

### Features
- Display average fuel prices in Portugal.
- Show the last update date for average prices.
- List stations by fuel type:
  - Diesel
  - Gasoline 95
  - Premium gasoline 95
  - Gasoline 98
  - Premium gasoline 98
  - 2-stroke gasoline mix
- Show per-station Google Maps directions links (`Direções -> Abrir`).
- Responsive layout for desktop and mobile.

### Tech Stack
- Python
- Streamlit
- Pandas
- Requests

### Performance
- Environment-configurable cache (defaults: 15 minutes for average prices and 60 minutes for station lists).
- Parallel page fetching (`ThreadPoolExecutor`) with dynamic pagination to avoid unnecessary requests.
- HTTP connection reuse with `requests.Session()`.
- Automatic retry on transient API/network failures.
- Clustered map rendering for better readability with large datasets.

### Run locally
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-user>/combustiveis-pt.git
   cd combustiveis-pt
   ```
2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install streamlit pandas requests python-dotenv
   ```
4. Create the `.env` file with your API key:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and set:
   ```bash
   APIABERTA_API_KEY=<YOUR_API_KEY>
   ```
   (Optional) Fine-tune performance in `.env`:
   ```bash
   AVG_PRICES_CACHE_TTL_SECONDS=900
   STATIONS_CACHE_TTL_SECONDS=3600
   APIABERTA_STATIONS_MAX_WORKERS=12
   APIABERTA_STATIONS_MAX_PAGES=60
   ```
5. Run the app:
   ```bash
   streamlit run app.py
   ```

### Project structure
- `app.py`: main app interface.
- `components.py`: data-fetching and transformation helpers for prices and stations by fuel type.
