import serial
import time
import json
import os
import csv
from datetime import datetime

# --- Configurações ---
PASTA_ARMAZENAMENTO = os.path.join(os.path.dirname(__file__), '..', 'FASE_3-Armazenamento')
ARQUIVO_DADOS_BRUTOS = os.path.join(PASTA_ARMAZENAMENTO, 'dados_brutos.csv')
ARQUIVO_PARAMETROS = os.path.join(PASTA_ARMAZENAMENTO, 'parametros.json')

# Cabeçalho do CSV, correspondendo à ordem dos dados do Arduino
HEADERS = ["Volta", "Distancia", "Tempo de Volta", "Tempo Total"]

def get_config():
    """Lê o arquivo de parâmetros JSON."""
    try:
        with open(ARQUIVO_PARAMETROS, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existe ou está corrompido, assume que está parado
        return {'rodando': False}

def coletor_de_dados():
    """Função principal que roda em loop para coletar dados da serial."""
    ser = None
    csv_writer = None
    csv_file = None

    print("Coletor Serial iniciado.")
    print(f"Aguardando comandos de início em: {ARQUIVO_PARAMETROS}")
    
    while True:
        config = get_config()
        rodando = config.get('rodando', False)

        if rodando:
            # Se deve rodar, mas a serial não está conectada, conecta
            if ser is None:
                try:
                    porta = config['porta_serial']
                    baud = config['baud_rate']
                    print(f"Iniciando coleta na porta {porta} a {baud} bps.")
                    ser = serial.Serial(porta, baud, timeout=1.0)
                    ser.flushInput() # Limpa o buffer de entrada

                    # Prepara o arquivo CSV
                    csv_file = open(ARQUIVO_DADOS_BRUTOS, 'w', newline='', encoding='utf-8')
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(HEADERS) # Escreve o cabeçalho

                except serial.SerialException as e:
                    print(f"ERRO: Não foi possível abrir a porta serial '{config.get('porta_serial')}'. Detalhes: {e}")
                    # Desliga no arquivo de parametros para o dashboard saber do erro
                    config['rodando'] = False 
                    with open(ARQUIVO_PARAMETROS, 'w') as f: json.dump(config, f)
                    ser = None
                    continue
                except KeyError:
                    print("ERRO: 'porta_serial' ou 'baud_rate' não encontrado nos parâmetros.")
                    config['rodando'] = False 
                    with open(ARQUIVO_PARAMETROS, 'w') as f: json.dump(config, f)
                    ser = None
                    continue

            # Se a serial estiver conectada, lê os dados
            try:
                line = ser.readline().decode('utf-8').strip()
                if line and line.split(',')[0].isdigit(): # Checa se a linha começa com um número (Volta)
                    dados = line.split(',')
                    if len(dados) == len(HEADERS):
                        csv_writer.writerow(dados)
                        csv_file.flush() # Garante que os dados sejam escritos no disco imediatamente
                        print(f"Volta registrada: {line}")
                    else:
                        print(f"AVISO: Linha com formato incorreto recebida: {line}")
            except (UnicodeDecodeError, IndexError) as e:
                print(f"AVISO: Erro ao processar linha da serial. {e}")
            except serial.SerialException as e:
                print(f"ERRO: Problema na comunicação serial. {e}")
                ser.close()
                ser = None

        else: # Se não estiver rodando
            if ser is not None and ser.is_open:
                ser.close()
                csv_file.close()
                ser = None
                csv_writer = None
                print("Coleta parada. Porta serial e arquivo fechados.")
            # Espera um pouco para não consumir CPU desnecessariamente
            time.sleep(1)

if __name__ == "__main__":
    if not os.path.exists(PASTA_ARMAZENAMENTO):
        os.makedirs(PASTA_ARMAZENAMENTO)
    coletor_de_dados()