# -*- coding: utf-8 -*-
"""
========================================================================
        SCRIPT 2: TRANSMISSOR LORA ADAPTATIVO
========================================================================

Este processo tem duas responsabilidades:
1.  Atuar como um cliente de dados, conectando-se ao 'coletor_can.py'
    para obter as informações de telemetria mais recentes.
2.  Gerenciar toda a lógica de comunicação LoRa bidirecional e adaptativa,
    enviando os dados para a base remota.
"""
# =======================================================================
# 1. IMPORTAÇÕES
# =======================================================================
import threading
import time
import struct
import socket
import json
import RPi.GPIO as GPIO
import serial

# =======================================================================
# 2. CONFIGURAÇÕES E CONSTANTES
# =======================================================================
# O caminho do socket foi ajustado para encontrar o arquivo na pasta 'Nivel_1_Coleta'.
# '..' sobe um nível (para 'Protocolo_LORA(Principal)').
# 'Nivel_1_Coleta' entra na pasta correta.
# 'telemetry_socket' é o nome do arquivo final.
SOCKET_FILE = os.path.join(os.path.dirname(__file__), '..', 'Nivel_1_Coleta', 'telemetry_socket')



# (Cole aqui TODAS as constantes e dicionários da seção 2 e 3 
#  do script 'telemetria_adaptativa_pi.py' da resposta anterior. 
#  Isso inclui: LoRa, Protocolo, QoS, Prioridades e Formatos)
# ...
PRIORITY_1_SENSORS = ["ECU Batery voltage", "ECU Average O2", "Engine temperature", "Oil pressure", "Fuel pressure"]
#... etc

# =======================================================================
# 3. DADOS COMPARTILHADOS E SINCRONIZAÇÃO
# =======================================================================
# Dicionário que será preenchido com os dados recebidos do coletor
latest_telemetry_data = {}
telemetry_lock = threading.Lock() # Trava para este dicionário

last_downlink_rssi = -80
last_downlink_rssi_lock = threading.Lock()

# =======================================================================
# 4. CLASSE DE CONTROLE DO LORA E220
# =======================================================================
# (Cole aqui a classe LoraE220 completa da resposta anterior, com o método
#  receive_packet)
class LoraE220:
    # ...

# =======================================================================
# 5. LÓGICA DO CLIENTE DE DADOS (IPC)
# =======================================================================
def data_client_thread():
    """
    Thread dedicada a manter uma conexão com o servidor de dados (coletor CAN)
    e a atualizar continuamente o dicionário de telemetria local.
    """
    while True:
        try:
            print("[Cliente de Dados] Tentando conectar ao servidor do coletor CAN...")
            client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client_socket.connect(SOCKET_FILE)
            print("[Cliente de Dados] Conectado! Recebendo dados...")
            
            buffer = ""
            while True:
                # Recebe os dados em pedaços (chunks)
                data_chunk = client_socket.recv(1024).decode('utf-8')
                if not data_chunk:
                    # Conexão fechada pelo servidor
                    break
                
                buffer += data_chunk
                # Processa mensagens completas (delimitadas por \n)
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    # Deserializa o JSON para um dicionário Python
                    received_data = json.loads(message)
                    
                    # Atualiza o dicionário global de forma segura
                    with telemetry_lock:
                        global latest_telemetry_data
                        latest_telemetry_data = received_data
                        
        except (ConnectionRefusedError, FileNotFoundError):
            print("[Cliente de Dados] Servidor não encontrado. Tentando novamente em 5 segundos...")
            time.sleep(5)
        except Exception as e:
            print(f"ERRO no cliente de dados: {e}. Reconectando...")
            time.sleep(5)
        finally:
            client_socket.close()

# =======================================================================
# 6. LÓGICA DO GERENCIADOR LORA
# =======================================================================
# (Cole aqui as funções lora_manager_thread, process_incoming_lora_packet,
#  build_lora_packet, e verify_checksum da resposta anterior, SEM ALTERAÇÕES NA LÓGICA INTERNA)
# A única pequena mudança é de onde ela pega os dados.

def lora_manager_thread(lora_module):
    print("[LoRa Manager] Thread iniciada.")
    send_interval = 1.0 / TAXA_ENVIO_LORA_HZ
    last_send_time = time.time()

    while True:
        # 1. Ouvir LoRa
        incoming_packet = lora_module.receive_packet()
        if incoming_packet:
            process_incoming_lora_packet(incoming_packet)

        # 2. Enviar LoRa
        if time.time() - last_send_time >= send_interval:
            # ... (Toda a lógica adaptativa de decisão de prioridade é mantida) ...

            # MUDANÇA: Pega os dados do dicionário local, que é atualizado pelo cliente IPC
            with telemetry_lock:
                data_copy = latest_telemetry_data.copy()
            
            if not data_copy:
                # Se ainda não recebeu nenhum dado do coletor, espera
                continue

            # ... (O resto da função continua igual, construindo e enviando o pacote) ...
            packet_to_send = build_lora_packet(data_copy, sensors_to_send, message_id)
            lora_module.send_packet(LORA_DEST_ID, LORA_CANAL, packet_to_send)
            last_send_time = time.time()
        
        time.sleep(0.01)

# ... (demais funções do gerenciador LoRa aqui) ...

# =======================================================================
# 7. EXECUÇÃO PRINCIPAL
# =======================================================================
if __name__ == '__main__':
    print("--- INICIANDO PROCESSO TRANSMISSOR LORA ---")

    # Inicia a thread que busca os dados do processo coletor
    client_thread = threading.Thread(target=data_client_thread, daemon=True)
    client_thread.start()

    # Espera um pouco para garantir que a primeira coleta de dados ocorra
    print("Aguardando os primeiros dados do coletor...")
    time.sleep(2) 
    
    # Inicializa o módulo LoRa
    lora = LoraE220(SERIAL_PORT_LORA, SERIAL_BAUDRATE_LORA, PIN_M0, PIN_M1, PIN_AUX)
    lora.setup()

    # Inicia a thread que gerencia a comunicação LoRa
    lora_thread = threading.Thread(target=lora_manager_thread, args=(lora,), daemon=True)
    lora_thread.start()
    
    print("--- Threads iniciadas. O sistema está operacional. ---")
    print("Pressione Ctrl+C para sair.")
    
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\nSainal de interrupção recebido. Encerrando o programa...")
    finally:
        lora.cleanup()
        print("Programa encerrado.")