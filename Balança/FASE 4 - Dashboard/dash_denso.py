from datetime import datetime, timedelta
import io
import os
import random
import threading
import time
import dash
from dash import dcc, html, dash_table
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State
import plotly.express as px
import glob
from dash.dash_table.Format import Format
from pathlib import Path # Adicionado

lock = threading.Lock()
df_new = pd.DataFrame(columns = ['Load Cell', 'Weight', 'Mean', 'interval'])  
df_all = pd.DataFrame({
    'Load Cell': pd.Series(dtype='str'),
    'Weight': pd.Series(dtype='float'),
    'Mean': pd.Series(dtype='float'),
    'interval': pd.Series(dtype='int')
})  
gradient_colors = ["#7EC8E3", "#4682B4", "#1E3A5F", "#0D1B2A"]

# --- Definição de Caminhos Relativos ---
# Encontra o diretório raiz do projeto ("Balança"), subindo um nível a partir do script
project_root = Path(__file__).parent.parent

# Define o caminho para a pasta de dados do IDLE
DIRETORIO_DADOS = project_root / "FASE 2 - IDLE" / "dados"

# Define o caminho para o arquivo Excel de setups
excel_path = project_root / "FASE 4 - Dashboard" / "Resultados - Aeromap.xlsx"

# --- Fim da Definição de Caminhos ---

ULTIMO_ARQUIVO = None
ULTIMA_POSICAO = 0
OUTPUT_FILENAME = "saved_data.txt"

# Adicione estas variáveis globais no início do arquivo
buffer = io.StringIO()
last_save_timestamp = None
current_measurements = []

try:
    setups = pd.ExcelFile(excel_path)
    sheet_names = [i for i in setups.sheet_names if 'Setup Asa' in i]
except FileNotFoundError:
    print(f"Arquivo Excel não encontrado em: {excel_path}")
    print("Usando lista vazia para setups")
    sheet_names = []
except Exception as e:
    print(f"Erro ao carregar arquivo Excel: {e}")
    sheet_names = []


def get_latest_data_file():
    "Encontra o arquivo de dados mais recente no diretório"
    list_of_files = glob.glob(os.path.join(DIRETORIO_DADOS, '*.txt'))
    if not list_of_files:
        return None
    return max(list_of_files, key=os.path.getctime)

def read_new_data():
    global ULTIMO_ARQUIVO, ULTIMA_POSICAO, df_all
    
    current_file = get_latest_data_file()
    
    if not current_file:
        print("Nenhum arquivo de dados encontrado.")
        return
    
    if current_file != ULTIMO_ARQUIVO:
        ULTIMO_ARQUIVO = current_file
        ULTIMA_POSICAO = 0
    
    try:
        with open(current_file, 'r') as f:
            f.seek(ULTIMA_POSICAO)
            new_lines = f.readlines()
            ULTIMA_POSICAO = f.tell()
            
            current_time = datetime.now()
            for line in new_lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith("LEITURA;"):
                    values = line.split(';')[1:5]
                    if len(values) == 4:
                        cells = ['FL', 'FR', 'RL', 'RR']
                        for i, valor in enumerate(values):
                            try:
                                valor_float = float(valor)
                                new_row = pd.DataFrame({
                                    "Load Cell": [cells[i]],
                                    "Weight": valor_float,
                                    "Mean": 0,
                                    "interval": 0,
                                    "timestamp": current_time
                                }).astype({
                                    'Weight': 'float', 
                                    'Mean': 'float', 
                                    'interval': 'int',
                                    'timestamp': 'datetime64[ns]'
                                })
                                with lock:
                                    df_all = pd.concat([df_all, new_row], ignore_index=True)
                            except ValueError:
                                print(f"Valor inválido: {valor}")
                # Adicione aqui outros tipos de linha se necessário (ex: MEDIA)
    
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")

# Inicializando o app Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX, dbc.icons.FONT_AWESOME])

# Layout do app
app.layout = html.Div(
    style={'minHeight': '100vh', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'padding': '20px'},
    children=[
        html.H1("WIND TUNNEL ANALYSIS", style={'fontSize': '36px', 'fontWeight': 'bold', 'fontFamily':'math'}),
        html.Div(
            style={'display': 'flex', 'width': '80%'},
            children=[
                # 📋 Coluna Esquerda - Lista de Dados
                html.Div(
                    style={'flex': 1,  'padding': '20px', 'margin': '10px', 'borderRadius': '10px', 'boxShadow': '2px 2px 10px rgba(0,0,0,0.3)', 'fontFamily':'math'},
                    children=[
                        html.H3("Load Cell Data"),
                        dcc.Dropdown(sheet_names, id='setups-dropdown', placeholder="Select setup"),
                        html.Div(style = {'padding-bottom':'10px'}),
                        dcc.Dropdown([i for i in range(0,110,10)], id='velocity-dropdown', placeholder="Select velocity"),
                        html.Div(style = {'padding-bottom':'10px'}),
                        dash_table.DataTable(
                            id='table',
                            data=df_new.to_dict('records'),
                            columns=[
                                {"name": "Load Cell", "id": "Load Cell"},
                                {"name": "Weight (N)", "id": "Weight", "type": "numeric", 
                                 "format": {"specifier": ",.3f"}},  # Formato com 1 casa decimal
                                {"name": "Mean (N)", "id": "Mean", "type": "numeric", 
                                 "format": {"specifier": ",.3f"}}   # Formato com 1 casa decimal
                            ],
                            style_table={'width': '100%'},
                            style_header={
                                'fontWeight': 'bold',
                                'textAlign': 'center',
                                'backgroundColor': '#f8f9fa'
                            },
                            style_cell={
                                'textAlign': 'center',
                                'padding': '10px',
                                'border': '1px solid #415A77'
                            },
                        ),
                        dcc.Interval(id='interval-component', interval=1000, n_intervals=0),
                        html.Div(style={'padding': '5px'}),
                        dbc.Row(
                            [
                                dbc.Col(dbc.Button('💾 Save Data', id='save_data'), width="auto"),
                                dbc.Col(dbc.Button('⬇️ Download Data', id='download_data_button'), width="auto"),
                            ],
                            justify="start",  # centraliza os botões
                            className="mb-3"
                        ),
                        dbc.Modal(
                            [
                                dbc.ModalHeader(dbc.ModalTitle("Data Saved")),
                                dbc.ModalBody("Keep going."),
                            ],
                            id="modal_saved",
                            size="sm",
                            is_open=False,
                        ),
                        dcc.Download(id="download_data"),
                        dcc.Graph(id='graph-load-cell'),
                        # html.Div(
                            # style={'flex': 1, 'padding': '20px', 'margin': '10px', 'borderRadius': '10px', 'boxShadow': '2px 2px 10px rgba(0,0,0,0.3)', 'textAlign': 'center'},
                            # children=[
                            # dcc.Graph(id='balance', style={'width': '100%'}),
                            # ]
                        # ),
                    ]
                ),
                # 🏎️ Coluna Central - Carro com valores
                html.Div(
                    style={'flex': 1.5,  'padding': '20px', 'margin': '10px', 'borderRadius': '10px', 'boxShadow': '2px 2px 10px rgba(0,0,0,0.3)', 'textAlign': 'center'},
                    children=[
                        html.Img(src="/assets/fsae-removebg-2.png", style={'width': '100%', 'background': 'none', 'padding-top':'100px'}),
                        html.Div(
                            style={'display': 'flex', 'justifyContent': 'space-around', 'marginTop': '10px'},
                            children=[
                                html.Div(id='fl', 
                                         style={
                                                'position': 'absolute',
                                                'top': '180px',
                                                'left': '870px',
                                                'width': '80px',
                                                'height': '30px',
                                                'backgroundColor': 'rgb(35,75,175,0.3)',
                                                'fontSize': '24px',
                                                'fontWeight': 'bold',
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'justifyContent': 'center'
                                         }),
                                html.Div(id='fr', 
                                         style={
                                                'position': 'absolute',
                                                'top': '180px',
                                                'left': '1175px',
                                                'width': '80px',
                                                'height': '30px',
                                                'backgroundColor': 'rgb(35,75,175,0.3)',
                                                'fontSize': '24px',
                                                'fontWeight': 'bold',
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'justifyContent': 'center'
                                            },
                                         ),
                                html.Div(id='rl', 
                                         style={
                                                'position': 'absolute',
                                                'top': '520px',
                                                'left': '870px',
                                                'width': '80px',
                                                'height': '30px',
                                                'backgroundColor': 'rgb(35,75,175,0.3)',
                                                'fontSize': '24px',
                                                'fontWeight': 'bold',
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'justifyContent': 'center'
                                            },
                                         ),
                                html.Div(id='rr', 
                                         style={
                                                'position': 'absolute',
                                                'top': '520px',
                                                'left': '1175px',
                                                'width': '80px',
                                                'height': '30px',
                                                'backgroundColor': 'rgb(35,75,175,0.3)',
                                                'fontSize': '24px',
                                                'fontWeight': 'bold',
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'justifyContent': 'center'
                                            },
                                         ),
                            ]
                        ),
                        html.H6('Front/Back Loaded', style={'padding-top':'30px'}),
                        html.H6(id='balanceamento', style={'padding-top':'5px'}),
                        html.Div([
                            html.Div(id='barra-balanceamento', style={
                                'height': '10px',
                                'width': '500px',
                                'borderRadius': '5px',
                                'marginTop': '5px',
                                'marginBottom': '5px',
                                'display': 'flex',
                                'transition': 'all 0.3s ease-in-out'
                            })
                        ], style={'display': 'flex', 'justifyContent': 'center'})
                        # dcc.Graph(id='balance', style={'height': '220px'})
                    ]
                ),
            ]
        ),
        #  html.Div(
        #     style={'display': 'flex', 'width': '80%', 'marginTop': '20px'},
        #     children=[
        #         # 🏎️ Coluna Central - Carro com valores
        #         html.Div(
        #             style={'flex': 1, 'padding': '20px', 'margin': '10px', 'borderRadius': '10px', 'boxShadow': '2px 2px 10px rgba(0,0,0,0.3)', 'textAlign': 'center'},
        #             children=[
        #                 dcc.Graph(id='heatmap', style={'width': '100%'}, config={'displayModeBar': False}),
        #             ]
        #         ),
        #     ]
        # ),
    ]
)

@app.callback(
    Output('table', 'data'),
    Output('graph-load-cell', 'figure'),
    # Output('heatmap', 'figure'),
    Output('barra-balanceamento', 'children'),
    Output('balanceamento', 'children'),
    Output('fl', 'children'),
    Output('fr', 'children'),
    Output('rl', 'children'),
    Output('rr', 'children'),
    Input('interval-component', 'n_intervals')
)

def update_graph(n):
    global df_all

    read_new_data()

    try:
        with lock:
            df_copy = df_all.copy()

        if not df_copy.empty:
            # Garante que temos os últimos valores de cada célula e calcula médias
            df_latest = pd.DataFrame()
            for cell in ['FL', 'FR', 'RL', 'RR']:
                cell_data = df_copy[df_copy['Load Cell'] == cell]
                if not cell_data.empty:
                    last_row = cell_data.iloc[[-1]]
                    last_row['Mean'] = cell_data['Weight'].mean()  # Calcula média
                    df_latest = pd.concat([df_latest, last_row])

            # Preenche valores faltantes
            df_latest.fillna(0, inplace=True)

            fl = df_latest[df_latest['Load Cell'] == 'FL']['Weight'].values[0] if 'FL' in df_latest['Load Cell'].values else 0
            fr = df_latest[df_latest['Load Cell'] == 'FR']['Weight'].values[0] if 'FR' in df_latest['Load Cell'].values else 0
            rr = df_latest[df_latest['Load Cell'] == 'RR']['Weight'].values[0] if 'RR' in df_latest['Load Cell'].values else 0
            rl = df_latest[df_latest['Load Cell'] == 'RL']['Weight'].values[0] if 'RL' in df_latest['Load Cell'].values else 0

        else:
            fl, fr, rr, rl = 0, 0, 0, 0
            df_latest = pd.DataFrame(columns=['Load Cell', 'Weight', 'Mean'])

        # Cálculos de balanceamento
        total = fl + fr + rr + rl
        if total > 0:
            pct_frente = round((fl + fr) * 100 / total, 2)
            pct_traseira = round(100 - pct_frente, 2)
        else:
            pct_frente = 50
            pct_traseira = 50
        # Gradiente da barra: da esquerda (frente) para a direita (traseira)
        barra = [
            html.Div(style={
                'width': f'{pct_frente}%',
                'backgroundColor': gradient_colors[0],
                'border-start-start-radius': '5px',
                'border-end-start-radius': '5px',
                'height': '100%'
            }),
            html.Div(style={
                'width': f'{pct_traseira}%',
                'border-start-end-radius': '5px',
                'border-end-end-radius': '5px',
                'backgroundColor': gradient_colors[1],
                'height': '100%'
            })
        ]

        # Gráfico
        fig_historico = go.Figure()
        colors = gradient_colors[:4]
        for i, cell in enumerate(['FL', 'FR', 'RL', 'RR']):
            cell_data = df_copy[df_copy['Load Cell'] == cell]
            if not cell_data.empty:
                fig_historico.add_trace(go.Scatter(
                    y=cell_data['Weight'], 
                    name=cell, 
                    line=dict(color=colors[i]),
                    mode='lines+markers'
                ))
        fig_historico.update_layout(
            height=300,
            title='Histórico de Cargas',
            xaxis_title='Medições',
            yaxis_title='Carga (N)',
            showlegend=True
        )

        # Criar Heatmap
        # fig_heatmap = go.Figure(data=go.Heatmap(
        #     z=zi,
        #     x=xi,
        #     y=yi,
        #     colorscale='Jet',
        #     colorbar=dict(title='Carga (N)')
        # ))
        # fig_heatmap.update_layout(
        #     title='Distribuição Longitudinal de Carga no Carro',
        #     xaxis=dict(
        #         title='Longitudinal (m)',
        #         showgrid=False,
        #         zeroline=False,
        #         showline=False,
        #         showticklabels=True,
        #         range=[xi.min(), xi.max()],
        #         constrain='domain',
        #         scaleanchor=None
        #     ),
        #     yaxis=dict(
        #         title='Lateral (m)',
        #         showgrid=False,
        #         zeroline=False,
        #         showline=False,
        #         showticklabels=True,
        #         range=[yi.min(), yi.max()],
        #         scaleanchor=None
        #     ),
        #     plot_bgcolor='rgba(0,0,0,0)',  # fundo da área de plotagem transparente
        #     paper_bgcolor='rgba(0,0,0,0)',  # fundo do canvas transparente
        #     margin=dict(l=0, r=0, t=40, b=0),  # margens mínimas
        # )
        return (
            df_latest.to_dict('records'),
            fig_historico,
            barra,
            f'{pct_frente}% | {pct_traseira}%',
            f'{fl:,.1f}',  # Usando vírgula como separador de milhar
            f'{fr:,.1f}',
            f'{rl:,.1f}',
            f'{rr:,.1f}'
        )
    except Exception as e:
        print(f"Erro na atualização: {e}")
        return dash.no_update

@app.callback(
    Output("download_data", "data"),
    Output("modal_saved", "is_open"),
    Input("save_data", "n_clicks"),
    Input("download_data_button", "n_clicks"),
    State("setups-dropdown", "value"),
    State("velocity-dropdown", "value"),
    State("modal_saved", "is_open"),
    prevent_initial_call=True,
)
def download_csv(n_clicks_save, n_clicks_download, setup, velocity, is_open):
    global df_all, buffer, last_save_timestamp

    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, False

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    output_file = "wind_tunnel_data.csv"

    if button_id == "save_data" and n_clicks_save:
        # Verifica se setup e velocity foram fornecidos
        if not setup or velocity is None:
            print("Setup e velocidade são obrigatórios para salvar dados")
            return dash.no_update, False

        # Cria cabeçalho do bloco
        now = datetime.now()
        block_header = (
            f"Exported at: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Setup: {setup}\n"
            f"Velocity: {velocity} km/h\n"
            f"Timestamp,Load Cell,Weight\n"
        )
        
        # Prepara os dados das células
        with lock:
            # Filtra dados desde o último salvamento
            if last_save_timestamp is None:
                df_to_save = df_all.copy()
            else:
                df_to_save = df_all[df_all['timestamp'] > last_save_timestamp]

            # Agrupa por timestamp para garantir conjuntos completos
            timestamps = sorted(df_to_save['timestamp'].unique())
            block_content = ""
            
            for ts in timestamps:
                ts_data = df_to_save[df_to_save['timestamp'] == ts]
                for cell in ['FL', 'FR', 'RL', 'RR']:
                    cell_data = ts_data[ts_data['Load Cell'] == cell]
                    if not cell_data.empty:
                        row = cell_data.iloc[0]
                        formatted_ts = row['timestamp'].strftime("%H:%M:%S")
                        block_content += f"{formatted_ts},{cell},{row['Weight']:.3f}\n"

            # Atualiza o timestamp do último salvamento
            last_save_timestamp = now

        # Adiciona o bloco ao arquivo
        try:
            mode = "a" if os.path.exists(output_file) else "w"
            with open(output_file, mode, encoding="utf-8") as f:
                f.write(block_header)
                f.write(block_content)
                f.write("\n")  # Linha em branco entre blocos
            print(f"Dados salvos em {output_file}")
            return dash.no_update, True

        except Exception as e:
            print(f"Erro ao salvar arquivo: {e}")
            return dash.no_update, False

    elif button_id == "download_data_button" and n_clicks_download:
        try:
            if os.path.exists(output_file):
                # Cria nome único para download
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                download_filename = f"wind_tunnel_data_{timestamp}.csv"
                
                # Renomeia arquivo atual para download
                os.rename(output_file, download_filename)
                
                # Limpa os dados globais e reset do timestamp
                with lock:
                    df_all = pd.DataFrame(columns=['Load Cell', 'Weight', 'Mean', 'interval', 'timestamp'])
                    buffer = io.StringIO()
                    last_save_timestamp = None
                
                return dcc.send_file(download_filename), False
            else:
                print("Nenhum arquivo encontrado para download")
                return dash.no_update, False

        except Exception as e:
            print(f"Erro durante download: {e}")
            return dash.no_update, False

    return dash.no_update, False

# Rodar o app
if __name__ == '__main__':
    ULTIMO_ARQUIVO = get_latest_data_file()
    if ULTIMO_ARQUIVO:
        ULTIMA_POSICAO = os.path.getsize(ULTIMO_ARQUIVO)
    
    app.run(debug=True)