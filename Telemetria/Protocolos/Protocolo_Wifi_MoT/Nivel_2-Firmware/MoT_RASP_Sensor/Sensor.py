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
    """
    Executa um comando no sistema para obter o RSSI de um cliente conectado.
    Agora com mensagens de debug detalhadas.
    """
    interface = "wlan0" # Interface WiFi da Pi
    command = ["iw", "dev", interface, "station", "dump"]
    
    try:
        # Executa o comando e captura a saída
        result = subprocess.check_output(command, text=True, stderr=subprocess.PIPE)
        
        # --- DEBUG: Imprime a saída completa do comando ---
        print("\n--- Saida do comando 'iw' ---")
        print(result)
        print("----------------------------")

        station_block_started = False
        for line in result.splitlines():
            # Procura pela linha que identifica a estação pelo IP do cliente
            if client_ip in line:
                station_block_started = True
            
            # Uma vez que encontramos o bloco do nosso cliente, procuramos pelo sinal
            if station_block_started and "signal" in line:
                # Extrai o valor do sinal, ex: '	signal avg:	-42 dBm'
                rssi = int(line.split(':')[1].strip().split(' ')[0])
                print(f"[Debug RSSI] Valor encontrado: {rssi} dBm")
                return rssi
                
        print("[Debug RSSI] Cliente encontrado, mas informacao de 'signal avg' nao localizada.")
        return 0

    except FileNotFoundError:
        print("ERRO DE DEBUG: O comando 'iw' nao foi encontrado. Instale com 'sudo apt-get install iw'")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"ERRO DE DEBUG: O comando 'iw' falhou com o erro: {e.stderr}")
        return 0
    except Exception as e:
        print(f"ERRO DE DEBUG: Erro inesperado ao tentar obter o RSSI: {e}")
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