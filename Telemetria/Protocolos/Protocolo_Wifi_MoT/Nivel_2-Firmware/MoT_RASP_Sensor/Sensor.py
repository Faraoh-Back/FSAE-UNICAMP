# =======================================================================
#               Servidor MoT WiFi - Raspberry Pi
# =======================================================================
import socket
import struct
import time
import subprocess

# --- MUDANÇA: O servidor agora ouve em '0.0.0.0' ---
# Isso significa que ele aceitará conexões de qualquer interface de rede (WiFi, Ethernet, etc.)
# Não importa qual IP seu celular dê para a Pi, o servidor estará ouvindo nele.
SERVER_IP = "0.0.0.0" 
SERVER_PORT = 4210
TAMANHO_PACOTE = 52

# IDs dos dispositivos
PI_ID = 100
ESP_ID = 1

# Mapeamento dos índices do pacote
RSSI_UPLINK = 0
RECEIVER_ID = 8
TRANSMITTER_ID = 10

def get_client_rssi(client_ip):
    """Executa um comando no sistema para obter o RSSI de um cliente conectado."""
    try:
        result = subprocess.check_output(["iw", "dev", "wlan0", "station", "dump"], text=True)
        station_block = None
        for line in result.splitlines():
            if client_ip in line:
                station_block = line
            if station_block and "signal avg" in line:
                rssi = int(line.split(':')[1].strip().split(' ')[0])
                return rssi
    except Exception:
        pass
    return 0

# --- Execução Principal ---
if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SERVER_IP, SERVER_PORT))

    print(f"--- Servidor MoT WiFi Iniciado na porta {SERVER_PORT} ---")
    print("Aguardando pacotes do ESP8266 via rede do celular...")
    print("Meu nome na rede e: raspberrypi.local")

    while True:
        try:
            data, address = sock.recvfrom(1024)
            client_ip = address[0]
            uplink_rssi = get_client_rssi(client_ip)
            
            print(f"\nPacote recebido de {client_ip}. RSSI (Uplink): {uplink_rssi} dBm")
            
            pacote_resposta = bytearray(TAMANHO_PACOTE)
            struct.pack_into('<h', pacote_resposta, RSSI_UPLINK, uplink_rssi)
            struct.pack_into('<B', pacote_resposta, RECEIVER_ID, ESP_ID)
            struct.pack_into('<B', pacote_resposta, TRANSMITTER_ID, PI_ID)
            
            sock.sendto(pacote_resposta, address)
            print(f"Resposta enviada para {client_ip}.")
            
        except Exception as e:
            print(f"Ocorreu um erro no loop principal: {e}")
            time.sleep(1)