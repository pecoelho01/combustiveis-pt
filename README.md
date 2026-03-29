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
- Cache semanal por chave de semana (dados mantidos estáveis durante a semana e renovados automaticamente à segunda-feira).
- Pré-carregamento semanal automático em background (preços + postos por combustível).
- Recolha de páginas em paralelo (`ThreadPoolExecutor`) para acelerar a listagem de postos.
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
5. Executar a aplicação:
   ```bash
   streamlit run app.py
   ```

### Estrutura
- `app.py`: interface principal da aplicação.
- `components.py`: funções de recolha/processamento de preços e postos por combustível.
- `.github/workflows/weekly-prewarm.yml`: cron externo (GitHub Actions) para pré-aquecer a app semanalmente.

### Cron Externo (Pré-warm semanal)
- O workflow `Weekly Streamlit Prewarm` abre a app com browser headless todas as segundas-feiras às 03:00 UTC (aprox. 04:00 em Lisboa no horário de verão).
- Para configurar a URL da tua app, define no GitHub:
  - `Settings -> Secrets and variables -> Actions -> Variables`
  - Variável: `STREAMLIT_APP_URL`
  - Exemplo: `https://combustiveis-pt.streamlit.app/`
- Podes testar manualmente em:
  - `Actions -> Weekly Streamlit Prewarm -> Run workflow`

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
- Weekly cache keyed by week start (data stays stable during the week and refreshes automatically on Monday).
- Automatic weekly background pre-warm (prices + stations by fuel type).
- Parallel page fetching (`ThreadPoolExecutor`) to speed up station loading.
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
5. Run the app:
   ```bash
   streamlit run app.py
   ```

### Project structure
- `app.py`: main app interface.
- `components.py`: data-fetching and transformation helpers for prices and stations by fuel type.
- `.github/workflows/weekly-prewarm.yml`: external cron (GitHub Actions) to prewarm the app weekly.

### External Cron (Weekly prewarm)
- The `Weekly Streamlit Prewarm` workflow opens the app with a headless browser every Monday at 03:00 UTC (~04:00 Lisbon during DST).
- To configure your app URL, set in GitHub:
  - `Settings -> Secrets and variables -> Actions -> Variables`
  - Variable: `STREAMLIT_APP_URL`
  - Example: `https://combustiveis-pt.streamlit.app/`
- You can trigger it manually from:
  - `Actions -> Weekly Streamlit Prewarm -> Run workflow`
