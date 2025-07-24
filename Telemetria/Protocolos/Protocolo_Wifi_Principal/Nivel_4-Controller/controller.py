import os
import sys
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# =======================================================================
#               MUDANÇA 1: Encontrar o model.py
# =======================================================================
# Adiciona a pasta irmã 'Nivel_3-Model' ao caminho de busca do Python
# para que possamos importar o 'model.py' que está lá.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Nivel_3-Model'))
from model import TelemetryModel # Agora a importação funciona!

# --- Suas credenciais do Supabase aqui (sem alteração) ---
SUPABASE_URL = "https://mpicdzosenzmkkagzcwr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1waWNkem9zZW56bWtrYWd6Y3dyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMwOTUxMjksImV4cCI6MjA2ODY3MTEyOX0.xa1Sy2c8j2Iu3HvO8x4CqPj_NmelIPWxnIsSr7dl2rk"

# Inicializa o FastAPI e o nosso modelo
app = FastAPI()
telemetry_model = TelemetryModel(SUPABASE_URL, SUPABASE_KEY)

# =======================================================================
#         MUDANÇA 2: Apontar para a Nova Pasta do Frontend
# =======================================================================
# Define o caminho correto para a pasta 'static' dentro de 'Nivel_5-View'
static_path = os.path.join(os.path.dirname(__file__), '..', 'Nivel_5-View', 'static')
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Define o caminho correto para a pasta que contém os templates HTML
templates_path = os.path.join(os.path.dirname(__file__), '..', 'Nivel_5-View')
templates = Jinja2Templates(directory=templates_path)


# Configura o CORS (sem alteração)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# =======================================================================
#                  ROTAS DO FRONTEND (PÁGINAS HTML)
# =======================================================================
# A rota para o index.html agora aponta para o arquivo dentro da pasta Nivel_5-View
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# A rota para o all_graphs.html também foi ajustada
@app.get("/all_graphs", response_class=HTMLResponse)
async def read_all_graphs(request: Request):
    return templates.TemplateResponse("all_graphs.html", {"request": request})

# =======================================================================
#                       ROTAS DA API (DADOS)
# =======================================================================
@app.get("/api/status")
def get_status():
    status = telemetry_model.get_telemetry_status()
    return {"rodando": status}

@app.post("/api/start")
def start_telemetry():
    if telemetry_model.set_telemetry_status(True):
        return JSONResponse(content={"message": "Telemetria iniciada."}, status_code=200)
    return JSONResponse(content={"message": "Falha ao iniciar."}, status_code=500)

@app.post("/api/stop")
def stop_telemetry():
    if telemetry_model.set_telemetry_status(False):
        return JSONResponse(content={"message": "Telemetria parada."}, status_code=200)
    return JSONResponse(content={"message": "Falha ao parar."}, status_code=500)

@app.get("/api/dados_live")
def get_live_data(limit: int = 100):
    """Endpoint para fornecer dados recentes para os gráficos."""
    data = telemetry_model.get_live_data(limit)
    return data

@app.get("/api/estatisticas")
def get_statistics():
    """Endpoint que calcula e fornece as estatísticas completas."""
    stats = telemetry_model.get_statistics()
    return stats