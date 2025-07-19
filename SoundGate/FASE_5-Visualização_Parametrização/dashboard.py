import dash
from dash import dcc, html, dash_table, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import serial.tools.list_ports
import json
import os
import time
from datetime import datetime
import subprocess # Para chamar o script de processamento

# --- Configurações ---
PASTA_ARMAZENAMENTO = os.path.join(os.path.dirname(__file__), '..', 'FASE_3-Armazenamento')
ARQUIVO_DADOS_BRUTOS = os.path.join(PASTA_ARMAZENAMENTO, 'dados_brutos.csv')
ARQUIVO_PARAMETROS = os.path.join(PASTA_ARMAZENAMENTO, 'parametros.json')
ARQUIVO_METRICAS = os.path.join(PASTA_ARMAZENAMENTO, 'metricas.json')
SCRIPT_PROCESSADOR = os.path.join(os.path.dirname(__file__), '..', 'FASE_4-Tratamento_Dados', 'processador.py')

# Garante que a pasta de armazenamento exista
if not os.path.exists(PASTA_ARMAZENAMENTO):
    os.makedirs(PASTA_ARMAZENAMENTO)

# --- Inicialização do App Dash ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
app.title = "SoundGate Dashboard"

# --- Layout do Dashboard ---
def criar_layout():
    portas_seriais = [port.device for port in serial.tools.list_ports.comports()]
    
    return dbc.Container(fluid=True, children=[
        dcc.Store(id='store-parametros'),
        dcc.Interval(id='intervalo-atualizacao', interval=2 * 1000, n_intervals=0),
        dcc.Download(id="download-csv"),

        # --- Título ---
        html.H1("SoundGate Dashboard FSAE", className="text-center text-primary mt-3 mb-4"),

        # --- Painel de Controle ---
        dbc.Card(className="mb-4", body=True, children=[
            dbc.Row([
                dbc.Col(dbc.Label("Porta Serial:"), width=2),
                dbc.Col(dcc.Dropdown(id='dropdown-porta-serial', options=portas_seriais, value=portas_seriais[0] if portas_seriais else None), width=4),
                dbc.Col(dbc.Label("Baud Rate:"), width=2),
                dbc.Col(dcc.Input(id='input-baud-rate', type='number', value=9600, className="form-control"), width=4),
            ]),
            dbc.Row(className="mt-3", children=[
                dbc.Col(dbc.Button("▶ INICIAR COLETA", id='btn-iniciar', color="success", className="w-100"), width=6),
                dbc.Col(dbc.Button("■ PARAR COLETA", id='btn-parar', color="danger", className="w-100"), width=6),
            ]),
            dbc.Row(className="mt-3", children=[
                dbc.Col(html.Div(id='status-coleta', className="text-center fw-bold"))
            ])
        ]),

        # --- Visualização de Dados ---
        dbc.Row([
            # Coluna da Tabela de Voltas
            dbc.Col(width=7, children=[
                dbc.Card(body=True, children=[
                    html.H4("Tabela de Voltas", className="card-title"),
                    html.Div(id='tabela-container', children=[
                        dash_table.DataTable(
                            id='tabela-voltas',
                            style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'fontWeight': 'bold'},
                            style_data={'backgroundColor': 'rgb(50, 50, 50)', 'color': 'white'},
                            style_cell={'textAlign': 'center', 'padding': '5px'},
                        )
                    ])
                ])
            ]),
            # Coluna das Métricas
            dbc.Col(width=5, children=[
                dbc.Card(body=True, children=[
                    html.H4("Métricas Gerais", className="card-title"),
                    html.Div(id='metricas-display')
                ])
            ])
        ]),
        
        # --- Download e Parametrização ---
        dbc.Card(className="mt-4", body=True, children=[
            html.H4("Download e Parametrização", className="card-title"),
            html.P("Adicione parâmetros para nomear o arquivo de download."),
            html.Div(id='parametros-container', children=[]),
            dbc.Button("Adicionar Parâmetro", id='btn-add-param', n_clicks=0, color="secondary", size="sm", className="me-2 mt-2"),
            dbc.Button("Baixar CSV", id='btn-baixar-csv', n_clicks=0, color="info", className="mt-2"),
        ])
    ])

app.layout = criar_layout

# --- Callbacks ---

# 1. Controlar início/parada da coleta
@app.callback(
    Output('status-coleta', 'children'),
    Input('btn-iniciar', 'n_clicks'),
    Input('btn-parar', 'n_clicks'),
    State('dropdown-porta-serial', 'value'),
    State('input-baud-rate', 'value'),
    prevent_initial_call=True
)
def controlar_coleta(n_iniciar, n_parar, porta, baud):
    ctx = callback_context
    if not ctx.triggered:
        return "Aguardando comando..."

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'btn-iniciar':
        if not porta:
            return dbc.Alert("ERRO: Nenhuma porta serial selecionada!", color="warning")
        
        config = {'rodando': True, 'porta_serial': porta, 'baud_rate': int(baud)}
        with open(ARQUIVO_PARAMETROS, 'w') as f:
            json.dump(config, f)
        
        # Limpa arquivos antigos
        if os.path.exists(ARQUIVO_DADOS_BRUTOS): os.remove(ARQUIVO_DADOS_BRUTOS)
        if os.path.exists(ARQUIVO_METRICAS): os.remove(ARQUIVO_METRICAS)
            
        return dbc.Alert(f"Coleta iniciada na porta {porta}", color="success")
        
    elif button_id == 'btn-parar':
        config = {'rodando': False}
        with open(ARQUIVO_PARAMETROS, 'w') as f:
            json.dump(config, f)
        return dbc.Alert("Coleta parada.", color="danger")

# 2. Atualizar tabela de voltas e acionar o processador de dados
@app.callback(
    Output('tabela-voltas', 'columns'),
    Output('tabela-voltas', 'data'),
    Output('metricas-display', 'children'),
    Input('intervalo-atualizacao', 'n_intervals'),
    State('status-coleta', 'children')
)
def atualizar_dados_e_metricas(n, status):
    try:
        df = pd.read_csv(ARQUIVO_DADOS_BRUTOS)
        columns = [{"name": i, "id": i} for i in df.columns]
        data = df.to_dict('records')
        
        # Chama o script processador em background
        subprocess.run(['python', SCRIPT_PROCESSADOR, PASTA_ARMAZENAMENTO], check=True)
        
        # Lê as métricas geradas
        with open(ARQUIVO_METRICAS, 'r') as f:
            metricas = json.load(f)
        
        metricas_layout = [
            dbc.Row([dbc.Col(html.Strong("Total de Voltas:")), dbc.Col(metricas['total_voltas'])]),
            dbc.Row([dbc.Col(html.Strong("Melhor Volta (s):")), dbc.Col(metricas['melhor_volta'])]),
            dbc.Row([dbc.Col(html.Strong("Pior Volta (s):")), dbc.Col(metricas['pior_volta'])]),
            dbc.Row([dbc.Col(html.Strong("Média das Voltas (s):")), dbc.Col(metricas['media_voltas'])]),
            dbc.Row([dbc.Col(html.Strong("Desvio Padrão (s):")), dbc.Col(metricas['desvio_padrao'])]),
        ]
        
    except (FileNotFoundError, pd.errors.EmptyDataError):
        # Se os arquivos não existem ou estão vazios
        return [], [], "Nenhum dado coletado ainda."
    except Exception as e:
        return [], [], f"Erro ao processar dados: {e}"
        
    return columns, data, metricas_layout

# 3. Adicionar campos de parâmetro dinamicamente
@app.callback(
    Output('parametros-container', 'children'),
    Input('btn-add-param', 'n_clicks'),
    State('parametros-container', 'children')
)
def adicionar_parametro(n_clicks, children):
    novo_param = dbc.Row(className="mb-2", children=[
        dbc.Col(dcc.Input(placeholder='Nome do Parâmetro (ex: Mola)', type='text', className="form-control"), width=6),
        dbc.Col(dcc.Input(placeholder='Valor (ex: 300)', type='text', className="form-control"), width=6)
    ])
    children.append(novo_param)
    return children

# 4. Baixar CSV com nome parametrizado
@app.callback(
    Output('download-csv', 'data'),
    Input('btn-baixar-csv', 'n_clicks'),
    State('parametros-container', 'children'),
    prevent_initial_call=True
)
def baixar_csv(n_clicks, params_children):
    try:
        df = pd.read_csv(ARQUIVO_DADOS_BRUTOS)
        
        # Constrói o nome do arquivo
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename_parts = [now]
        
        if params_children:
            for child in params_children:
                try:
                    nome = child['props']['children'][0]['props']['children']['props']['value']
                    valor = child['props']['children'][1]['props']['children']['props']['value']
                    if nome and valor:
                        filename_parts.append(f"{nome.replace(' ', '_')}:{valor.replace(' ', '_')}")
                except (KeyError, TypeError):
                    continue
        
        filename = "_".join(filename_parts) + ".csv"
        
        return dcc.send_data_frame(df.to_csv, filename, index=False)
        
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return None # Não faz nada se não houver dados

if __name__ == '__main__':
    app.run_server(debug=True)