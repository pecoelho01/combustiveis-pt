# Combustiveis PT

## PT

Aplicação em Streamlit para consultar preços médios de combustíveis em Portugal, com dados obtidos da API aberta.

Demo online: [https://combustiveis-pt.streamlit.app/](https://combustiveis-pt.streamlit.app/)

### Funcionalidades
- Mostrar tabela com preços médios de combustíveis em Portugal.
- Mostrar data da última atualização disponível na API.
- Interface simples com `selectbox` para escolher a funcionalidade.

### Stack
- Python
- Streamlit
- Pandas
- Requests

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
   pip install streamlit pandas requests
   ```
4. Executar a aplicação:
   ```bash
   streamlit run app.py
   ```

### Estrutura
- `app.py`: interface principal da aplicação.
- `components.py`: funções auxiliares para obter e transformar dados da API.

---

## EN

Streamlit app to check average fuel prices in Portugal using data from an open API.

Live demo: [https://combustiveis-pt.streamlit.app/](https://combustiveis-pt.streamlit.app/)

### Features
- Display a table with average fuel prices in Portugal.
- Show the last update date returned by the API.
- Simple UI with a `selectbox` to choose the feature.

### Tech Stack
- Python
- Streamlit
- Pandas
- Requests

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
   pip install streamlit pandas requests
   ```
4. Run the app:
   ```bash
   streamlit run app.py
   ```

### Project structure
- `app.py`: main app interface.
- `components.py`: helper functions to fetch and transform API data.
