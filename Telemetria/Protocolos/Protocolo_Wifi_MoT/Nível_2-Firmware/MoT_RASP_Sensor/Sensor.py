# =======================================================================
#               Servidor MoT WiFi - Raspberry Pi
# =======================================================================
import socket
import struct
import time
import subprocess

# --- Configurações da Rede e do Pacote ---
SERVER_IP = "192.168.4.1"  # IP padrão da Pi em modo AP
SERVER_PORT = 4210         # Porta para a comunicação UDP
TAMANHO_PACOTE = 52

# IDs dos dispositivos
PI_ID = 100
ESP_ID = 1

# Mapeamento dos índices do pacote (mantendo a estrutura do seu protocolo)
RSSI_UPLINK = 0
RSSI_DOWNLINK = 2
RECEIVER_ID = 8
TRANSMITTER_ID = 10

def get_client_rssi(client_ip):
    """
    Executa um comando no sistema para obter o RSSI de um cliente conectado.
    Retorna o valor em dBm.
    """
    try:
        # O comando 'iw' é mais moderno e preciso para obter informações de estações
        result = subprocess.check_output(["iw", "dev", "wlan0", "station", "dump"], text=True)
        
        # Procura pelas linhas relevantes no output do comando
        station_block = None
        for line in result.splitlines():
            if client_ip in line:
                station_block = line
            if station_block and "signal avg" in line:
                # Extrai o valor do sinal, ex: '	signal avg:	-42 dBm'
                rssi = int(line.split(':')[1].strip().split(' ')[0])
                return rssi
    except Exception as e:
        # print(f"Aviso: Nao foi possivel obter o RSSI do cliente. {e}")
        pass # Ignora o erro se o cliente ainda nao estiver listado
    return 0 # Retorna 0 se nao encontrar

# --- Execução Principal ---
if __name__ == "__main__":
    # Cria um socket UDP
    # AF_INET = Protocolo de internet (IPv4)
    # SOCK_DGRAM = Datagrama (UDP)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Associa o socket ao IP e porta do servidor
    sock.bind((SERVER_IP, SERVER_PORT))

    print(f"--- Servidor MoT WiFi Iniciado em {SERVER_IP}:{SERVER_PORT} ---")
    print("Aguardando pacotes do ESP8266...")

    while True:
        try:
            # Espera receber um pacote (o buffer de 1024 é mais que suficiente)
            # data, address = sock.recvfrom(1024)
            data, address = sock.recvfrom(1024)

            # address[0] é o IP do cliente (ESP8266)
            client_ip = address[0]

            # 1. Mede o RSSI do pacote que acabou de chegar
            uplink_rssi = get_client_rssi(client_ip)
            
            print(f"\nPacote recebido de {client_ip}. RSSI (Uplink): {uplink_rssi} dBm")
            
            # 2. Monta o pacote de resposta
            pacote_resposta = bytearray(TAMANHO_PACOTE)

            # Preenche os campos do pacote
            # 'h' é o formato para um short signed integer (2 bytes), ideal para RSSI
            # '<' indica little-endian byte order, comum em microcontroladores
            struct.pack_into('<h', pacote_resposta, RSSI_UPLINK, uplink_rssi)
            struct.pack_into('<B', pacote_resposta, RECEIVER_ID, ESP_ID) # Destinatário é o ESP
            struct.pack_into('<B', pacote_resposta, TRANSMITTER_ID, PI_ID) # Remetente é o Pi
            
            # 3. Envia a resposta de volta para o ESP
            sock.sendto(pacote_resposta, address)
            print(f"Resposta enviada para {client_ip}.")
            
        except Exception as e:
            print(f"Ocorreu um erro no loop principal: {e}")
            time.sleep(1)