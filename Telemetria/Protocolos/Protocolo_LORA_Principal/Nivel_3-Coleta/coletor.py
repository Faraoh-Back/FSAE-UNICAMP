import serial
import time
import json
import os
import csv
from datetime import datetime

# --- Configurações ---
PASTA_ARMAZENAMENTO = os.path.join(os.path.dirname(__file__), '..', 'Nivel_4-Armazenamento')
ARQUIVO_DADOS_BRUTOS = os.path.join(PASTA_ARMAZENAMENTO, 'DADOS_BRUTOS.csv')
ARQUIVO_PARAMETROS = os.path.join(PASTA_ARMAZENAMENTO, 'PARAMETROS.json')

# Cabeçalho do CSV, correspondendo à ordem dos dados na string serial
HEADERS = [
    "timestamp", "ECU RPM", "MAP", "Engine temperature", "Oil pressure", "Fuel pressure",
    "ECU Batery voltage", "Steering Angle (Placeholder)", "Gforce -(lateral)",
    "Traction speed", "TPS", "Brake pressure", "Suspension Travel (Placeholder)",
    "Gear", "ECU Average O2", "ECU Injection Bank A Time"
]
NUM_SENSORES = len(HEADERS) - 1

def get_config():
    """Lê o arquivo de parâmetros JSON."""
    try:
        with open(ARQUIVO_PARAMETROS, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'rodando': False, 'porta_serial': '', 'baud_rate': 115200} # Baud rate ajustado

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
                    baud_rate = config.get('baud_rate', 115200) # Pega o baud rate da config
                    print(f"Iniciando coleta na porta {config['porta_serial']} a {baud_rate} bps.")
                    ser = serial.Serial(config['porta_serial'], baud_rate, timeout=1.0)
                    
                    with open(ARQUIVO_DADOS_BRUTOS, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(HEADERS)
                except serial.SerialException as e:
                    print(f"ERRO: Não foi possível abrir a porta serial '{config['porta_serial']}'. Detalhes: {e}")
                    config['rodando'] = False 
                    with open(ARQUIVO_PARAMETROS, 'w') as f: json.dump(config, f, indent=4)
                    ser = None
                    continue

            if ser and ser.is_open:
                try:
                    # >>>>> ALTERAÇÃO AQUI <<<<<
                    # Envia um byte de requisição para o Arduino simulador
                    ser.write(b'R') # 'R' de "Request"

                    # Aguarda e lê a resposta
                    line = ser.readline().decode('utf-8').strip()
                    
                    if line.startswith('<') and line.endswith('>'):
                        data_str = line[1:-1]
                        valores = data_str.split(';')

                        if len(valores) == NUM_SENSORES:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                            dados_numericos = [float(v) for v in valores]
                            linha_csv = [timestamp] + dados_numericos
                            
                            with open(ARQUIVO_DADOS_BRUTOS, 'a', newline='') as f:
                                writer = csv.writer(f)
                                writer.writerow(linha_csv)
                            
                            print(f"Dados Simulados Recebidos: RPM={dados_numericos[0]:.0f}, Temp Motor={dados_numericos[2]:.1f}")
                        else:
                            print(f"AVISO: Linha com formato incorreto recebida. Esperados {NUM_SENSORES} valores, recebidos {len(valores)}.")
                    else:
                        if line: # Só imprime se a linha não estiver vazia
                            print(f"AVISO: Dado recebido não está no formato esperado: {line}")

                except (UnicodeDecodeError, ValueError) as e:
                    print(f"AVISO: Erro ao decodificar ou converter dados da serial. Erro: {e}")
                except serial.SerialException as e:
                    print(f"ERRO: Problema na porta serial. {e}")
                    ser.close()
                    ser = None
        else:
            if ser and ser.is_open:
                ser.close()
                print("Coleta parada. Porta serial fechada.")
                ser = None
            time.sleep(1)

if __name__ == "__main__":
    if not os.path.exists(PASTA_ARMAZENAMENTO):
        os.makedirs(PASTA_ARMAZENAMENTO)
    print("Nível 3: Coletor de Telemetria (MODO SIMULADOR) - Iniciado.")
    print(f"Aguardando comandos de início em: {ARQUIVO_PARAMETROS}")
    coletor_de_dados()