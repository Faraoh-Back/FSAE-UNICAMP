# -*- coding: utf-8 -*-
"""
========================================================================
        SCRIPT 1: COLETOR E SERVIDOR DE DADOS CAN
========================================================================

Este processo tem duas responsabilidades:
1.  Ler e decodificar continuamente os dados da rede CAN da ECU em uma
    thread dedicada.
2.  Atuar como um servidor de dados, oferecendo as informações de
    telemetria mais recentes para outros processos locais via um
    Socket de Domínio Unix.
"""

# =======================================================================
# 1. IMPORTAÇÕES
# =======================================================================
import threading
import time
import struct
import can
import socket
import json
import os

# =======================================================================
# 2. CONFIGURAÇÕES E CONSTANTES
# =======================================================================
CAN_INTERFACE = 'can0'
# O caminho do socket agora é relativo ao próprio diretório do script.
# __file__ é uma variável especial do Python que contém o caminho do arquivo atual.
# os.path.dirname(__file__) pega o diretório desse caminho.
# O resultado é que 'telemetry_socket' será criado dentro de 'Nivel_1_Coleta'.
SOCKET_FILE = os.path.join(os.path.dirname(__file__), 'telemetry_socket')


# (Cole aqui os dicionários MEASURE_ID_MAP e SIMPLIFIED_PACKET_MAP da resposta anterior)
MEASURE_ID_MAP = {
    # ...
}
SIMPLIFIED_PACKET_MAP = {
    # ...
}
HEADERS = [
    "ECU RPM", "MAP", "Engine temperature", "Oil pressure", "Fuel pressure",
    "ECU Batery voltage", "Steering Angle (Placeholder)", "Gforce -(lateral)",
    "Traction speed", "TPS", "Brake pressure", "Suspension Travel (Placeholder)",
    "Gear", "ECU Average O2", "ECU Injection Bank A Time"
]

# =======================================================================
# 3. DADOS COMPARTILHADOS E SINCRONIZAÇÃO
# =======================================================================
telemetry_data = {sensor: 0.0 for sensor in HEADERS}
telemetry_lock = threading.Lock()

# =======================================================================
# 4. LÓGICA DO LEITOR CAN (Thread)
# =======================================================================
# (Cole aqui as funções can_reader_thread, process_value, 
#  process_standard_broadcast, e process_simplified_packet da 
#  resposta anterior, sem nenhuma alteração)
def can_reader_thread():
    # ...
def process_value(raw_value, multiplier):
    # ...
def process_standard_broadcast(msg):
    # ...
def process_simplified_packet(msg):
    # ...

# =======================================================================
# 5. LÓGICA DO SERVIDOR DE DADOS (IPC)
# =======================================================================
def data_server():
    """
    Função principal que cria o socket, ouve por conexões e serve
    os dados de telemetria para o cliente (o script LoRa).
    """
    # Garante que o arquivo de socket antigo seja removido se o script
    # foi interrompido de forma anormal anteriormente.
    if os.path.exists(SOCKET_FILE):
        os.remove(SOCKET_FILE)

    # Cria o Socket de Domínio Unix
    # AF_UNIX: Família de sockets para comunicação local.
    # SOCK_STREAM: Comunicação baseada em fluxo (como TCP).
    server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    try:
        print(f"[Servidor de Dados] Criando socket em {SOCKET_FILE}")
        server_socket.bind(SOCKET_FILE)
        # Ouve por até 1 conexão pendente
        server_socket.listen(1)

        while True:
            print("[Servidor de Dados] Aguardando conexão do cliente (Transmissor LoRa)...")
            connection, client_address = server_socket.accept()
            print("[Servidor de Dados] Cliente conectado!")
            
            try:
                while True:
                    # Trava os dados para garantir uma cópia segura
                    with telemetry_lock:
                        data_to_send = telemetry_data.copy()
                    
                    # Serializa o dicionário para uma string JSON
                    # e depois para bytes, adicionando uma nova linha como delimitador.
                    serialized_data = json.dumps(data_to_send).encode('utf-8') + b'\n'
                    
                    # Envia os dados para o cliente
                    connection.sendall(serialized_data)
                    
                    # Pausa para não sobrecarregar o cliente
                    time.sleep(0.05) # Envia 20x por segundo

            except (BrokenPipeError, ConnectionResetError):
                print("[Servidor de Dados] Cliente desconectado.")
            finally:
                # Fecha a conexão atual e se prepara para uma nova
                connection.close()
                
    except Exception as e:
        print(f"ERRO CRÍTICO no servidor de dados: {e}")
    finally:
        # Limpeza final ao encerrar o script
        print("[Servidor de Dados] Encerrando e removendo arquivo de socket.")
        if os.path.exists(SOCKET_FILE):
            os.remove(SOCKET_FILE)

# =======================================================================
# 6. EXECUÇÃO PRINCIPAL
# =======================================================================
if __name__ == '__main__':
    print("--- INICIANDO PROCESSO COLETOR DE DADOS CAN ---")
    
    # Inicia a thread que lê o CAN Bus
    can_thread = threading.Thread(target=can_reader_thread, daemon=True)
    can_thread.start()
    
    # Inicia a função principal que serve os dados
    data_server()