import pandas as pd
import time
import json
import os

# --- Configurações ---
PASTA_ARMAZENAMENTO = os.path.join(os.path.dirname(__file__), '..', 'Nivel_4-Armazenamento')
ARQUIVO_DADOS_BRUTOS = os.path.join(PASTA_ARMAZENAMENTO, 'DADOS_BRUTOS.csv')
ARQUIVO_ESTATISTICAS = os.path.join(PASTA_ARMAZENAMENTO, 'ESTATISTICAS.json')
ARQUIVO_PARAMETROS = os.path.join(os.path.dirname(__file__), '..', 'Nivel_4-Armazenamento', 'PARAMETROS.json')

def get_config():
    #Lê o arquivo de parâmetros (JSON).
    try:
        with open(ARQUIVO_PARAMETROS, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"ERRO: O arquivo '{ARQUIVO_PARAMETROS}' não existe ou está vazio.")
        return {'rodando': False}

def processar_dados():
    #Lê o CSV de dados brutos e calcula estatísticas para cada sensor.
    try:
        df = pd.read_csv(ARQUIVO_DADOS_BRUTOS)
        if df.empty:
            return None
        
        # Calcula estatísticas para todas as colunas numéricas, pika
        stats = df.describe().to_dict()
        
        # Formata para um JSON mais limpo
        resultado = {col: {'media': data['mean'], 'min': data['min'], 'max': data['max'], 'desvio_padrao': data['std']} for col, data in stats.items()}
        return resultado

    except (FileNotFoundError, pd.errors.EmptyDataError):
        print(f"ERRO: O arquivo '{ARQUIVO_DADOS_BRUTOS}' não existe ou está vazio.")
        return None # Arquivo ainda não existe ou está vazio

def loop_processador():
    #Loop principal que verifica se deve processar os dados.
    while True:
        config = get_config()
        if config.get('rodando', False):
            estatisticas = processar_dados()
            if estatisticas:
                # Salva as estatísticas para o Nível 6 ler
                with open(ARQUIVO_ESTATISTICAS, 'w') as f:
                    json.dump(estatisticas, f, indent=4)
        
        time.sleep(1) # Roda o processamento a cada segundo

if __name__ == "__main__":
    print("Nível 5: Processador de Dados - Iniciado.")
    print(f"Monitorando dados em: {ARQUIVO_DADOS_BRUTOS}")
    loop_processador()