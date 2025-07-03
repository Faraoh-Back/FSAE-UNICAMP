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

lock = threading.Lock()
df_new = pd.DataFrame(columns=['Metais', 'Deformação', 'Médias'])  
df_all = pd.DataFrame({
    'Metais': pd.Series(dtype='str'),
    'Deformação': pd.Series(dtype='float'),
    'timestamp': pd.Series(dtype='datetime64[ns]')
})  
gradient_colors = ["#7EC8E3", "#4682B4", "#1E3A5F", "#0D1B2A"]

# Configurações do arquivo de dados
DIRETORIO_DADOS = r"C:\Users\Otaldo\OneDrive\Organizar Pessoal OneDrive\Documentos\FSAE_Metais\FASE 3 - Armazenamento"
ULTIMO_ARQUIVO = None
ULTIMA_POSICAO = 0
OUTPUT_FILENAME = "metal_deformation_data.csv"

# Add these global variables
buffer = io.StringIO()
last_save_timestamp = None
current_measurements = []

# Try to load Excel file for setups
try:
    excel_path = r"C:\Users\Otaldo\OneDrive\Organizar Pessoal OneDrive\Documentos\FSAE_Metais\FASE 4 - Dashboard\Resultados - Aeromap.xlsx"
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
                try:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if ';' in line and '[' in line:
                        values_part = line.split('[')[0]
                        values = values_part.split(';')
                        if len(values) == 2:
                            valor1 = float(values[0])
                            valor2 = float(values[1])
                            
                            new_rows = pd.DataFrame({
                                "Metais": ["1", "2"],
                                "Deformação": [valor1, valor2],
                                "timestamp": [current_time, current_time]
                            })
                            
                            with lock:
                                df_all = pd.concat([df_all, new_rows], ignore_index=True)
                except ValueError as ve:
                    print(f"Valor inválido na linha: {line} - Erro: {ve}")
                except Exception as e:
                    print(f"Erro processando linha: {line} - Erro: {e}")
                
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")

# Inicializando o app Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX, dbc.icons.FONT_AWESOME])

app.layout = html.Div(
    style={'minHeight': '100vh', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'padding': '20px'},
    children=[
        html.H1("ANÁLISE DE DEFORMAÇÃO", 
                style={'fontSize': '36px', 
                       'fontWeight': 'bold', 
                       'fontFamily': 'math'}),
        html.Div(
            style={'display': 'flex', 'width': '80%'},
            children=[
                # Coluna Esquerda - Tabela e Gráfico
                html.Div(
                    style={'flex': 1, 'padding': '20px', 'margin': '10px', 'borderRadius': '10px', 'boxShadow': '2px 2px 10px rgba(0,0,0,0.3)'},
                    children=[
                        html.H3("Dados de Deformação"),
                        dcc.Dropdown(sheet_names, id='setups-dropdown', placeholder="Select setup"),
                        html.Div(style={'padding-bottom':'10px'}),
                        dcc.Dropdown([i for i in range(0,110,10)], id='velocity-dropdown', placeholder="Select velocity"),
                        html.Div(style={'padding-bottom':'10px'}),
                        dash_table.DataTable(
                            id='table',
                            data=df_new.to_dict('records'),
                            columns=[
                                {"name": "Metais", "id": "Metais"},
                                {"name": "Deformação (mm)", "id": "Deformação", "type": "numeric", 
                                 "format": {"specifier": ",.3f"}},
                                {"name": "Médias (mm)", "id": "Médias", "type": "numeric", 
                                 "format": {"specifier": ",.3f"}}
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
                            justify="start",
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
                        dcc.Graph(id='graph-deformacao'),
                    ]
                ),
                # Coluna Direita - Visualização em Tempo Real
                html.Div(
                    style={'flex': 1, 'padding': '20px', 'margin': '10px', 'borderRadius': '10px', 'boxShadow': '2px 2px 10px rgba(0,0,0,0.3)', 'textAlign': 'center'},
                    children=[
                        html.Img(src="/assets/fsae-removebg-2.png", style={'width': '100%', 'background': 'none', 'padding-top': '100px'}),
                        html.Div(
                            style={'display': 'flex', 'justifyContent': 'space-around', 'marginTop': '10px'},
                            children=[
                                html.Div(id='metal1', 
                                         style={
                                            'position': 'absolute',
                                            'top': '180px',
                                            'left': '870px',
                                            'width': '80px',
                                            'height': '30px',
                                            'backgroundColor': 'rgba(35,75,175,0.3)',
                                            'fontSize': '24px',
                                            'fontWeight': 'bold',
                                            'display': 'flex',
                                            'alignItems': 'center',
                                            'justifyContent': 'center'
                                         }),
                                html.Div(id='metal2', 
                                         style={
                                            'position': 'absolute',
                                            'top': '520px',
                                            'left': '870px',
                                            'width': '80px',
                                            'height': '30px',
                                            'backgroundColor': 'rgba(35,75,175,0.3)',
                                            'fontSize': '24px',
                                            'fontWeight': 'bold',
                                            'display': 'flex',
                                            'alignItems': 'center',
                                            'justifyContent': 'center'
                                         }),
                            ]
                        ),
                    ]
                ),
            ]
        ),
    ]
)

@app.callback(
    Output('table', 'data'),
    Output('graph-deformacao', 'figure'),
    Output('metal1', 'children'),
    Output('metal2', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n):
    global df_all

    read_new_data()

    try:
        with lock:
            df_copy = df_all.copy()

        if not df_copy.empty:
            # Calcula as médias das últimas 10 medições para cada metal
            df_latest = pd.DataFrame()
            for metal in ['1', '2']:
                metal_data = df_copy[df_copy['Metais'] == metal]
                if not metal_data.empty:
                    last_row = metal_data.iloc[[-1]]
                    # Calcula média das últimas 10 medições
                    last_row['Médias'] = metal_data.tail(10)['Deformação'].mean()
                    df_latest = pd.concat([df_latest, last_row])

            # Preenche valores faltantes
            df_latest.fillna(0, inplace=True)

            metal1_val = df_latest[df_latest['Metais'] == '1']['Deformação'].values[0] if '1' in df_latest['Metais'].values else 0
            metal2_val = df_latest[df_latest['Metais'] == '2']['Deformação'].values[0] if '2' in df_latest['Metais'].values else 0

        else:
            metal1_val, metal2_val = 0, 0
            df_latest = pd.DataFrame(columns=['Metais', 'Deformação', 'Médias'])

        # Gráfico com apenas duas linhas (Metais 1 e 2)
        fig_deformacao = go.Figure()
        colors = ['#1E3A5F', '#4682B4']
        
        for i, metal in enumerate(['1', '2']):
            metal_data = df_copy[df_copy['Metais'] == metal]
            if not metal_data.empty:
                fig_deformacao.add_trace(go.Scatter(
                    y=metal_data['Deformação'], 
                    name=f'Metal {metal}', 
                    line=dict(color=colors[i]),
                    mode='lines+markers'
                ))
        
        fig_deformacao.update_layout(
            height=400,
            title='Histórico de Deformação',
            xaxis_title='Medições',
            yaxis_title='Deformação (mm)',
            showlegend=True
        )

        return (
            df_latest.to_dict('records'),
            fig_deformacao,
            f'{metal1_val:,.1f}',
            f'{metal2_val:,.1f}'
        )
    except Exception as e:
        print(f"Erro na atualização: {e}")
        return dash.no_update

# Add the save/download callback
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
    output_file = "metal_deformation_data.csv"

    if button_id == "save_data" and n_clicks_save:
        if not setup or velocity is None:
            print("Setup e velocidade são obrigatórios para salvar dados")
            return dash.no_update, False

        now = datetime.now()
        block_header = (
            f"Exported at: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Setup: {setup}\n"
            f"Velocity: {velocity} km/h\n"
            f"Timestamp,Metal,Deformacao\n"
        )
        
        with lock:
            if last_save_timestamp is None:
                df_to_save = df_all.copy()
            else:
                df_to_save = df_all[df_all['timestamp'] > last_save_timestamp]

            timestamps = sorted(df_to_save['timestamp'].unique())
            block_content = ""
            
            for ts in timestamps:
                ts_data = df_to_save[df_to_save['timestamp'] == ts]
                for metal in ['1', '2']:
                    metal_data = ts_data[ts_data['Metais'] == metal]
                    if not metal_data.empty:
                        row = metal_data.iloc[0]
                        formatted_ts = row['timestamp'].strftime("%H:%M:%S")
                        block_content += f"{formatted_ts},Metal {metal},{row['Deformação']:.3f}\n"

            last_save_timestamp = now

        try:
            mode = "a" if os.path.exists(output_file) else "w"
            with open(output_file, mode, encoding="utf-8") as f:
                f.write(block_header)
                f.write(block_content)
                f.write("\n")
            print(f"Dados salvos em {output_file}")
            return dash.no_update, True

        except Exception as e:
            print(f"Erro ao salvar arquivo: {e}")
            return dash.no_update, False

    elif button_id == "download_data_button" and n_clicks_download:
        try:
            if os.path.exists(output_file):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                download_filename = f"metal_deformation_data_{timestamp}.csv"
                
                os.rename(output_file, download_filename)
                
                with lock:
                    df_all = pd.DataFrame(columns=['Metais', 'Deformação', 'timestamp'])
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

if __name__ == '__main__':
    ULTIMO_ARQUIVO = get_latest_data_file()
    if ULTIMO_ARQUIVO:
        ULTIMA_POSICAO = os.path.getsize(ULTIMO_ARQUIVO)
    
    app.run(debug=True)