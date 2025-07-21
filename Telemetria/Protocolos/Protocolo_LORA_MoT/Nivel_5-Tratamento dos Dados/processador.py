import serial
import time
import json
import os
import threading

# --- Configurações ---
TAMANHO_PACOTE = 52
PASTA_ARMAZENAMENTO = os.path.join(os.path.dirname(__file__), '..', 'Nivel_4_Armazenamento')
ARQUIVO_DADOS_BRUTOS = os.path.join(PASTA_ARMAZENAMENTO, 'DADOS_BRUTOS.csv')
ARQUIVO_PARAMETROS = os.path.join(PASTA_ARMAZENAMENTO, 'PARAMETROS.json')

# --- Mapeamento do Pacote (Baseado no seu enum) ---
class BytesDoPacote:
    RSSI_UPLINK = 0
    LQI_UPLINK = 1
    RSSI_DOWNLINK = 2
    LQI_DOWNLINK = 3
    RECEIVER_ID = 8
    TRANSMITTER_ID = 10
    DL_COUNTER_MSB = 12
    DL_COUNTER_LSB = 13
    UL_COUNTER_MSB = 14
    UL_COUNTER_LSB = 15

def get_config():
    """Lê o arquivo de parâmetros."""
    try:
        with open(ARQUIVO_PARAMETROS, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Retorna um padrão seguro se o arquivo não existir ou estiver vazio
        return {'rodando': False, 'porta_serial': 'COM1', 'baud_rate': 115200, 'qtde_medidas': 100}

def decodificar_rssi(byte_rssi):
    """Converte o byte de RSSI de volta para dBm, conforme a lógica do firmware."""
    if byte_rssi > 128:
        return ((byte_rssi - 256) / 2.0) - 74
    else:
        return (byte_rssi / 2.0) - 74

def coletor_de_dados():
    """Função principal que roda em loop para coletar dados."""
    ser = None
    ultimo_pkt_ul = 0
    pacotes_enviados_dl = 0
    pacotes_recebidos_ul = 0
    
    while True:
        config = get_config()
        rodando = config.get('rodando', False)

        if rodando:
            # Inicializa ou atualiza a conexão serial se necessário
            if ser is None or ser.port != config['porta_serial'] or ser.baudrate != config['baud_rate'] or not ser.is_open:
                if ser and ser.is_open:
                    ser.close()
                try:
                    print(f"Iniciando coleta na porta {config['porta_serial']} a {config['baud_rate']} bps.")
                    ser = serial.Serial(config['porta_serial'], config['baud_rate'], timeout=1.0)
                    
                    # Reinicia contadores ao iniciar nova medição
                    ultimo_pkt_ul = 0
                    pacotes_enviados_dl = 0
                    pacotes_recebidos_ul = 0
                    
                    # Limpa o arquivo de dados para a nova sessão
                    with open(ARQUIVO_DADOS_BRUTOS, 'w') as f:
                        f.write("timestamp;rssi_uplink;rssi_downlink;pkt_enviado_dl;pkt_recebido_ul\n")

                except serial.SerialException as e:
                    print(f"Erro ao abrir porta serial: {e}")
                    # Desliga a flag para não tentar de novo imediatamente
                    config['rodando'] = False 
                    with open(ARQUIVO_PARAMETROS, 'w') as f:
                        json.dump(config, f, indent=4)
                    ser = None
                    continue

            # Construir e enviar pacote de Downlink (DL)
            pacote_tx = bytearray([1] * TAMANHO_PACOTE) # Pacote de exemplo
            pacotes_enviados_dl += 1
            pacote_tx[BytesDoPacote.DL_COUNTER_LSB] = pacotes_enviados_dl % 256
            
            ser.write(pacote_tx)

            # Ler pacote de Uplink (UL)
            pacote_rx = ser.read(TAMANHO_PACOTE)

            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            if len(pacote_rx) == TAMANHO_PACOTE:
                pacotes_recebidos_ul += 1
                rssi_ul = decodificar_rssi(pacote_rx[BytesDoPacote.RSSI_UPLINK])
                rssi_dl = decodificar_rssi(pacote_rx[BytesDoPacote.RSSI_DOWNLINK])
                
                print(f"[{timestamp}] Pacote Recebido | RSSI UL: {rssi_ul:.2f} dBm, RSSI DL: {rssi_dl:.2f} dBm")
                
                # Salvar dados brutos no CSV
                with open(ARQUIVO_DADOS_BRUTOS, 'a') as f:
                    f.write(f"{timestamp};{rssi_ul:.2f};{rssi_dl:.2f};{pacotes_enviados_dl};{pacotes_recebidos_ul}\n")
            else:
                print(f"[{timestamp}] Perda de pacote detectada.")
                # Mesmo em caso de perda, salvamos um registro para calcular o PSR corretamente
                with open(ARQUIVO_DADOS_BRUTOS, 'a') as f:
                    f.write(f"{timestamp};NaN;NaN;{pacotes_enviados_dl};{pacotes_recebidos_ul}\n")

            # Verifica se atingiu a quantidade de medidas
            if pacotes_enviados_dl >= config.get('qtde_medidas', 100):
                print("Quantidade de medidas atingida. Parando a coleta.")
                config['rodando'] = False
                with open(ARQUIVO_PARAMETROS, 'w') as f:
                    json.dump(config, f, indent=4)

        else:
            if ser and ser.is_open:
                ser.close()
                print("Coleta parada. Porta serial fechada.")
                ser = None
        
        time.sleep(1) # Intervalo entre os pacotes

if __name__ == "__main__":
    if not os.path.exists(PASTA_ARMAZENAMENTO):
        os.makedirs(PASTA_ARMAZENAMENTO)
    print("Nível 3: Coletor de Dados - Iniciado.")
    print(f"Aguardando comandos no arquivo: {ARQUIVO_PARAMETROS}")
    coletor_de_dados()