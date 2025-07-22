# nivel_3_tratamento_dados.py
import pandas as pd
import time
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

def get_config():
    """Lê o arquivo de parâmetros (JSON)."""
    try:
        with open(ARQUIVO_PARAMETROS, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'rodando': False} # Padrão seguro

def processar_dados_do_supabase():
    """Puxa os dados do Supabase e calcula estatísticas."""
    try:
        print("Buscando dados do Supabase...")
        # Seleciona todos os dados da tabela
        response = supabase.table(NOME_TABELA).select("*").execute()
        
        if not response.data:
            print("Nenhum dado encontrado no Supabase ainda.")
            return None

        # Converte os dados recebidos em um DataFrame do Pandas
        df = pd.DataFrame(response.data)
        
        # Remove colunas que não são de sensores
        df = df.drop(columns=['id', 'created_at'], errors='ignore')
        
        # Calcula estatísticas para todas as colunas numéricas
        stats = df.describe().to_dict()
        
        # Formata para um JSON mais limpo e legível
        resultado = {
            col: {
                'media': round(data.get('mean', 0), 2),
                'min': data.get('min', 0),
                'max': data.get('max', 0),
                'desvio_padrao': round(data.get('std', 0), 2)
            } for col, data in stats.items()
        }
        print("Estatísticas calculadas com sucesso.")
        return resultado

    except Exception as e:
        print(f"ERRO ao buscar ou processar dados do Supabase: {e}")
        return None

def loop_processador():
    """Loop principal que verifica se deve processar os dados."""
    while True:
        config = get_config()
        if config.get('rodando', False):
            estatisticas = processar_dados_do_supabase()
            if estatisticas:
                # Salva as estatísticas para o Nível 4 ler
                with open(ARQUIVO_ESTATISTICAS, 'w') as f:
                    json.dump(estatisticas, f, indent=4)
        
        # Pausa antes da próxima verificação
        time.sleep(5) # Roda o processamento a cada 5 segundos

if __name__ == "__main__":
    # Garante que a pasta de dados compartilhados exista
    if not os.path.exists(PASTA_DADOS):
        os.makedirs(PASTA_DADOS)
        
    print("Nível 3: Processador de Dados - Iniciado.")
    print(f"Monitorando o arquivo de controle: {ARQUIVO_PARAMETROS}")
    loop_processador()