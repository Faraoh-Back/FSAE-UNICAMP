import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import serial.tools.list_ports
import json
import os

# --- Configurações ---
PASTA_ARMAZENAMENTO = os.path.join(os.path.dirname(__file__), '..', 'Nivel_4-Armazenamento')
ARQUIVO_DADOS_BRUTOS = os.path.join(PASTA_ARMAZENAMENTO, 'DADOS_BRUTOS.csv')
ARQUIVO_PARAMETROS = os.path.join(PASTA_ARMAZENAMENTO, 'PARAMETROS.json')

# Lista de sensores (deve ser a mesma do coletor, exceto timestamp)
SENSORES = [
    "ECU RPM", "MAP", "Engine temperature", "Oil pressure", "Fuel pressure",
    "ECU Batery voltage", "Steering Angle (Placeholder)", "Gforce -(lateral)",
    "Traction speed", "TPS", "Brake pressure", "Suspension Travel (Placeholder)",
    "Gear", "ECU Average O2", "ECU Injection Bank A Time"
]

# --- Inicialização do App Dash ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# --- Layout do Dashboard ---
def criar_layout_controle():
    """Cria o painel de controle superior."""
    portas_seriais = [port.device for port in serial.tools.list_ports.comports()]
    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col(html.H4("Painel de Controle da Telemetria"), width=12, className="text-center mb-4"),
                dbc.Col([
                    dbc.Label("Porta Serial:"),
                    dcc.Dropdown(id='dropdown-porta-serial', options=portas_seriais, value=portas_seriais[0] if portas_seriais else None)
                ], width=3),
                dbc.Col([
                    dbc.Label("Baud Rate:"),
                    dcc.Input(id='input-baud-rate', type='number', value=115200, className="form-control")
                ], width=3),
                dbc.Col(
                    dbc.Button("INICIAR / PARAR TELEMETRIA", id='btn-iniciar-parar', color="primary", n_clicks=0, className="w-100"),
                    align="end", width=3
                ),
                dbc.Col(
                    dbc.Spinner(html.Div(id='status-telemetria'), color="light"),
                    align="center", width=3
                )
            ])
        ]),
        className="mb-4"
    )

def criar_layout_graficos():
    """Cria a grade de gráficos para todos os sensores."""
    graficos = [
        dbc.Col(dcc.Graph(id=f'graph-{sensor.replace(" ", "-")}'), width=4) for sensor in SENSORES
    ]
    return dbc.Row(graficos)

app.layout = dbc.Container([
    criar_layout_controle(),
    criar_layout_graficos(),
    dcc.Interval(id='intervalo-atualizacao', interval=1000, n_intervals=0) # Atualiza a cada 1 segundo
], fluid=True)


# --- Callbacks ---
@app.callback(
    Output('status-telemetria', 'children'),
    Input('btn-iniciar-parar', 'n_clicks'),
    [dash.dependencies.State('dropdown-porta-serial', 'value'),
     dash.dependencies.State('input-baud-rate', 'value')]
)
def controlar_telemetria(n_clicks, porta, baud):
    """Controla o início e a parada da coleta de dados."""
    ctx = dash.callback_context
    if not ctx.triggered:
        # Estado inicial
        with open(ARQUIVO_PARAMETROS, 'w') as f:
            json.dump({'rodando': False}, f)
        return dbc.Badge("PARADA", color="danger", className="ms-1")

    # Lê o estado atual para invertê-lo
    try:
        with open(ARQUIVO_PARAMETROS, 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {'rodando': False}
    
    novo_estado = not config.get('rodando', False)
    
    if novo_estado:
        if not porta:
            return dbc.Badge("ERRO: Porta não selecionada", color="warning", className="ms-1")
        config = {
            'rodando': True,
            'porta_serial': porta,
            'baud_rate': int(baud)
        }
        status_badge = dbc.Badge("RODANDO", color="success", className="ms-1")
    else:
        config = {'rodando': False}
        status_badge = dbc.Badge("PARADA", color="danger", className="ms-1")

    with open(ARQUIVO_PARAMETROS, 'w') as f:
        json.dump(config, f, indent=4)
        
    return status_badge


@app.callback(
    [Output(f'graph-{sensor.replace(" ", "-")}', 'figure') for sensor in SENSORES],
    Input('intervalo-atualizacao', 'n_intervals')
)
def atualizar_graficos(n):
    """Atualiza todos os gráficos com os dados mais recentes do CSV."""
    try:
        df = pd.read_csv(ARQUIVO_DADOS_BRUTOS, index_col='timestamp', parse_dates=True).tail(100) # Pega as últimas 100 amostras
    except (FileNotFoundError, pd.errors.EmptyDataError):
        # Retorna gráficos vazios se não houver dados
        return [go.Figure() for _ in SENSORES]

    figures = []
    for sensor in SENSORES:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df[sensor], mode='lines', name=sensor))
        fig.update_layout(
            title=sensor,
            template='plotly_dark',
            margin=dict(l=40, r=20, t=40, b=30),
            xaxis_title=None,
            yaxis_title=None,
            font=dict(size=10)
        )
        figures.append(fig)

    return figures


if __name__ == '__main__':
    if not os.path.exists(PASTA_ARMAZENAMENTO):
        os.makedirs(PASTA_ARMAZENAMENTO)
    # Garante que o arquivo de parâmetros exista no início
    with open(ARQUIVO_PARAMETROS, 'w') as f:
        json.dump({'rodando': False}, f)
        
    app.run_server(debug=True)