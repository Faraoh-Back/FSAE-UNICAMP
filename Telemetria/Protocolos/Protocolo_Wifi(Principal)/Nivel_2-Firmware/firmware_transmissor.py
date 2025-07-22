# enviar_csv_para_supabase.py (Nível 2 - MODO AO VIVO)
import os
import csv
import time
from supabase import create_client, Client

# --- Suas credenciais e constantes aqui ---
SUPABASE_URL = "https://mpicdzosenzmkkagzcwr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1waWNkem9zZW56bWtrYWd6Y3dyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMwOTUxMjksImV4cCI6MjA2ODY3MTEyOX0.xa1Sy2c8j2Iu3HvO8x4CqPj_NmelIPWxnIsSr7dl2rk" # Lembre-se de manter sua chave segura
CSV_FILE = os.path.join(os.path.dirname(__file__), '..', 'Nivel_1-Pré-Tratamento (Rasp)', 'telemetry_data.csv')
TABLE_NAME_DADOS = 'telemetria-sensores'
TABLE_NAME_CONTROLE = 'controle_telemetria'

# Inicializa o cliente do Supabase
print("Inicializando cliente Supabase...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("Conectado com sucesso!")

def deve_enviar_dados():
    """Verifica o interruptor 'coleta_ativa' no Supabase."""
    try:
        response = supabase.table(TABLE_NAME_CONTROLE).select('coleta_ativa').eq('id', 1).single().execute()
        return response.data and response.data.get('coleta_ativa', False)
    except Exception:
        return False

def get_total_linhas(filepath):
    """Conta o número de linhas em um arquivo."""
    try:
        with open(filepath, 'r') as f:
            return sum(1 for row in f)
    except FileNotFoundError:
        return 0

def main():
    linhas_ja_enviadas = 0
    telemetria_estava_ativa = False
    
    print(f"Nível 2 (Uploader MODO AO VIVO) iniciado. Monitorando o arquivo: {CSV_FILE}")
    print("Aguardando comando de inicio do dashboard...")

    while True:
        telemetria_ativa_agora = deve_enviar_dados()

        if telemetria_ativa_agora:
            # --- LÓGICA DE INÍCIO ---
            # Se a telemetria estava parada e acabou de ser ativada
            if not telemetria_estava_ativa:
                print("\nTelemetria INICIADA. Ignorando dados históricos...")
                # Pula para o final do arquivo atual, subtraindo o cabeçalho
                linhas_ja_enviadas = max(0, get_total_linhas(CSV_FILE) - 1)
                print(f"Começando a ler a partir da linha ~{linhas_ja_enviadas}.")
                telemetria_estava_ativa = True

            # --- LÓGICA DE ENVIO (igual à anterior) ---
            try:
                if not os.path.exists(CSV_FILE):
                    time.sleep(2)
                    continue

                with open(CSV_FILE, mode='r') as infile:
                    reader = csv.DictReader(infile)
                    
                    # Pula as linhas já processadas
                    for _ in range(linhas_ja_enviadas):
                        next(reader, None)

                    novas_linhas_contador = 0
                    for row in reader:
                        # (O dicionário data_to_insert permanece o mesmo)
                        data_to_insert = { "RPM": int(row.get("ECU RPM",0)), "TempMotor": float(row.get("Engine temperature",0)), # etc... }
                        
                        supabase.table(TABLE_NAME_DADOS).insert(data_to_insert).execute()
                        linhas_ja_enviadas += 1
                        novas_linhas_contador += 1

                    if novas_linhas_contador > 0:
                        print(f"{novas_linhas_contador} novas linhas enviadas para a nuvem.")
            
            except Exception as e:
                print(f"!! ERRO durante o envio: {e}")
        
        else: # Se a telemetria estiver desativada
            if telemetria_estava_ativa:
                print("\nEnvio para a nuvem PAUSADO pelo dashboard.")
                telemetria_estava_ativa = False
            
            print("Envio para a nuvem em pausa...", end="\r")
        
        time.sleep(5)

if __name__ == "__main__":
    main()