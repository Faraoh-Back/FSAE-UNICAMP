import serial
import time
import json
import os
import csv
from datetime import datetime

# --- Configurações ---
PASTA_ARMAZENAMENTO = os.path.join(os.path.dirname(__file__), '..', 'Nivel_4_Armazenamento')
ARQUIVO_DADOS_BRUTOS = os.path.join(PASTA_ARMAZENAMENTO, 'DADOS_BRUTOS.csv')
ARQUIVO_PARAMETROS = os.path.join(PASTA_ARMAZENAMENTO, 'PARAMETROS.json')

# Cabeçalho do CSV, correspondendo à ordem dos sensores do pacote
# (A ordem deve ser a mesma do firmware para garantir a consistência)
HEADERS = [
    "timestamp", "RPM", "MAP", "Engine Temp", "Oil Pressure", "Fuel Pressure",
    "Baterry Tension", "Sterring", "G Force", "Wheel Speed", "TPS",
    "Break Temp", "Break Pressure", "Susp Pressure", "Susp Travel",
    "Gear Position", "Oil Temp", "Water Temp"
]
NUM_SENSORES = len(HEADERS) - 1 # -1 por causa do timestamp

def get_config():
    """Lê o arquivo de parâmetros JSON."""
    try:
        with open(ARQUIVO_PARAMETROS, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'rodando': False, 'porta_serial': '', 'baud_rate': 9600}

def coletor_de_dados():
    """Função principal que roda em loop para coletar dados da serial."""
    ser = None
    
    while True:
        config = get_config()
        rodando = config.get('rodando', False)

        if rodando:
            if ser is None or ser.port != config['porta_serial'] or not ser.is_open:
                if ser and ser.is_open:
                    ser.close()
                try:
                    print(f"Iniciando coleta na porta {config['porta_serial']} a {config['baud_rate']} bps.")
                    ser = serial.Serial(config['porta_serial'], config['baud_rate'], timeout=1.0)
                    
                    # Cria o arquivo CSV com cabeçalho caso não exista
                    with open(ARQUIVO_DADOS_BRUTOS, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(HEADERS)
                except serial.SerialException as e:
                    print(f"ERRO: Não foi possível abrir a porta serial '{config['porta_serial']}'. Verifique a conexão. Detalhes: {e}")
                    config['rodando'] = False 
                    with open(ARQUIVO_PARAMETROS, 'w') as f: json.dump(config, f, indent=4)
                    ser = None
                    continue

            # Loop de leitura da serial
            if ser and ser.is_open:
                try:
                    line = ser.readline().decode('utf-8').strip()
                    if line.startswith('<') and line.endswith('>'):
                        # Remove os caracteres de início/fim e divide os dados
                        data_str = line[1:-1]
                        valores = data_str.split(';')

                        if len(valores) == NUM_SENSORES:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                            
                            # Converte valores para float, tratando erros
                            dados_numericos = [float(v) for v in valores]
                            
                            linha_csv = [timestamp] + dados_numericos
                            
                            with open(ARQUIVO_DADOS_BRUTOS, 'a', newline='') as f:
                                writer = csv.writer(f)
                                writer.writerow(linha_csv)
                            
                            print(f"Dados recebidos: RPM={dados_numericos[0]}, Temp Motor={dados_numericos[2]}")
                        else:
                            print(f"AVISO: Linha com formato incorreto recebida. Esperados {NUM_SENSORES} valores, recebidos {len(valores)}.")
                except (UnicodeDecodeError, ValueError) as e:
                    print(f"AVISO: Erro ao decodificar ou converter dados da serial. Linha: '{line if 'line' in locals() else ''}'. Erro: {e}")
                except serial.SerialException as e:
                    print(f"ERRO: Problema na porta serial. {e}")
                    ser.close()
                    ser = None
        else:
            if ser and ser.is_open:
                ser.close()
                print("Coleta parada. Porta serial fechada.")
                ser = None
            time.sleep(1) # Tempo de Espera antes de checar o arquivo de novo

if __name__ == "__main__":
    if not os.path.exists(PASTA_ARMAZENAMENTO):
        os.makedirs(PASTA_ARMAZENAMENTO)
    print("Nível 3: Coletor de Telemetria - Iniciado.")
    print(f"Aguardando comandos de início em: {ARQUIVO_PARAMETROS}")
    coletor_de_dados()