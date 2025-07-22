# nivel_4_visualizacao.py
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import json
import os
from supabase import create_client, Client

# --- Configurações ---
# Crie uma pasta para os arquivos de troca de informação
PASTA_DADOS = os.path.join(os.path.dirname(__file__), '..', 'Nivel_4-Armazenamento')
ARQUIVO_ESTATISTICAS = os.path.join(PASTA_DADOS, 'ESTATISTICAS.json')
ARQUIVO_PARAMETROS = os.path.join(PASTA_DADOS, 'PARAMETROS.json')

# --- CREDENCIAIS DO SUPABASE (COLOQUE AS SUAS AQUI) ---
SUPABASE_URL = "https://mpicdzosenzmkkagzcwr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1waWNkem9zZW56bWtrYWd6Y3dyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMwOTUxMjksImV4cCI6MjA2ODY3MTEyOX0.xa1Sy2c8j2Iu3HvO8x4CqPj_NmelIPWxnIsSr7dl2rk"
NOME_TABELA = "telemetria-sensores"

# Inicializa o cliente do Supabase
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"ERRO CRÍTICO: Falha ao conectar com o Supabase. Verifique a URL e a Chave. {e}")
    exit()

# Lista de sensores (deve corresponder aos nomes das colunas na sua tabela Supabase)
SENSORES = [
    "RPM", "MAP", "TempMotor", "PressOleo", "PressCombustivel",
    "TensaoBateria", "Estercamento", "ForcaG", "Velocidade", "TPS",
    "PressFreio", "CursoSuspensao", "Marcha", "Sonda", "TempInjecao"
]

# --- Inicialização do App Dash ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# --- Layout do Dashboard ---
def criar_layout_controle():
    """Cria o painel de controle simplificado."""
    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col(html.H4("Painel de Controle da Telemetria"), width=6, className="text-center"),
                dbc.Col(
                    dbc.Button("INICIAR / PARAR PROCESSAMENTO", id='btn-iniciar-parar', color="primary", n_clicks=0, className="w-100"),
                    align="center", width=3
                ),
                dbc.Col(
                    dbc.Spinner(html.Div(id='status-processamento'), color="light"),
                    align="center", width=3
                )
            ])
        ]), className="mb-4"
    )

def criar_layout_graficos():
    """Cria a grade de gráficos para todos os sensores."""
    graficos = [dbc.Col(dcc.Graph(id=f'graph-{sensor}'), width=4) for sensor in SENSORES]
    return dbc.Row(graficos)

app.layout = dbc.Container([
    criar_layout_controle(),
    criar_layout_graficos(),
    dcc.Interval(id='intervalo-atualizacao', interval=2000, n_intervals=0) # Atualiza a cada 2 segundos
], fluid=True)


# --- Callbacks ---
@app.callback(
    Output('status-processamento', 'children'),
    Input('btn-iniciar-parar', 'n_clicks')
)
def controlar_processamento(n_clicks):
    """
    Controla o Nível 3 (processamento local) E o Nível 2 (coleta remota na Pi)
    usando o Supabase como interruptor.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        # Garante que no estado inicial, tudo está parado
        supabase.table('controle_telemetria').update({'coleta_ativa': False}).eq('id', 1).execute()
        with open(ARQUIVO_PARAMETROS, 'w') as f: json.dump({'rodando': False}, f)
        return dbc.Badge("PARADO", color="danger", className="ms-1")

    # Lê o estado atual para invertê-lo
    try:
        response = supabase.table('controle_telemetria').select('coleta_ativa').eq('id', 1).single().execute()
        estado_atual = response.data['coleta_ativa']
    except Exception as e:
        print(f"Erro ao ler estado do Supabase: {e}")
        estado_atual = False # Assume parado em caso de erro

    novo_estado = not estado_atual
    
    try:
        # --- ATUALIZA O INTERRUPTOR NA NUVEM ---
        supabase.table('controle_telemetria').update({'coleta_ativa': novo_estado}).eq('id', 1).execute()
        print(f"Interruptor na nuvem definido para: {novo_estado}")
        
        # Atualiza também o arquivo local para o processador
        with open(ARQUIVO_PARAMETROS, 'w') as f:
            json.dump({'rodando': novo_estado}, f, indent=4)
        
        status_badge = dbc.Badge("RODANDO", color="success", className="ms-1") if novo_estado else dbc.Badge("PARADO", color="danger", className="ms-1")
        return status_badge
        
    except Exception as e:
        print(f"ERRO ao tentar mudar o estado da telemetria: {e}")
        return dbc.Badge("ERRO", color="warning", className="ms-1")


@app.callback(
    [Output(f'graph-{sensor}', 'figure') for sensor in SENSORES],
    Input('intervalo-atualizacao', 'n_intervals')
)
def atualizar_graficos(n):
    """Atualiza todos os gráficos com os dados mais recentes do Supabase."""
    try:
        # Pega as últimas 100 amostras do banco de dados, ordenadas por tempo
        response = supabase.table(NOME_TABELA).select("*").order('created_at', desc=True).limit(100).execute()
        df = pd.DataFrame(response.data)
        # Converte a coluna de tempo para o tipo datetime
        df['created_at'] = pd.to_datetime(df['created_at'])
    except Exception as e:
        print(f"Erro ao buscar dados para os graficos: {e}")
        # Retorna gráficos vazios se não houver dados
        return [go.Figure(layout={'template': 'plotly_dark', 'title': sensor}) for sensor in SENSORES]

    figures = []
    for sensor in SENSORES:
        if sensor not in df.columns:
            figures.append(go.Figure(layout={'template': 'plotly_dark', 'title': f'{sensor} (Sem dados)'}))
            continue
            
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['created_at'], y=df[sensor], mode='lines', name=sensor))
        fig.update_layout(
            title=sensor.replace("_", " ").title(),
            template='plotly_dark',
            margin=dict(l=40, r=20, t=40, b=30),
            xaxis_title=None, yaxis_title=None, font=dict(size=10)
        )
        figures.append(fig)

    return figures


if __name__ == '__main__':
    # Garante que a pasta e o arquivo de parâmetros existam no início
    if not os.path.exists(PASTA_DADOS):
        os.makedirs(PASTA_DADOS)
    with open(ARQUIVO_PARAMETROS, 'w') as f:
        json.dump({'rodando': False}, f)
        
    app.run_server(debug=True, host='0.0.0.0') # host='0.0.0.0' permite acesso na rede