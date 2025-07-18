# -*- coding: utf-8 -*-
"""
========================================================================
        SCRIPT ÚNICO: COLETOR CAN E ARMAZENADOR LOCAL
========================================================================

Este processo unificado tem duas responsabilidades:
1.  Ler e decodificar continuamente os dados da rede CAN da ECU.
2.  Armazenar os dados de telemetria mais recentes diretamente em um
    arquivo CSV local para consulta posterior pelo servidor WiFi.
"""

# =======================================================================
# 1. IMPORTAÇÕES
# =======================================================================
import threading
import time
import struct
import can
import json
import os
import csv

# =======================================================================
# 2. CONFIGURAÇÕES E CONSTANTES
# =======================================================================
CAN_INTERFACE = 'can0'
DATA_FILE = 'telemetry_data.csv' # Nome do arquivo para salvar os dados

# Dicionário de mapeamento de IDs da ECU para nomes de sensores
MEASURE_ID_MAP = {
    0: "ECU RPM",
    1: "MAP",
    2: "TPS",
    3: "Engine temperature",
    4.0: "ECU Average O2",
    5: "ECU Injection Bank A Time",
    6: "ECU Batery voltage",
    7: "Oil pressure",
    8: "Fuel pressure",
    9: "Gear"
}

# Mapeamento para o pacote simplificado de 4 bytes
SIMPLIFIED_PACKET_MAP = {
    "Brake pressure": (0, 10),       # Primeiro byte, multiplicador 10
    "Traction speed": (1, 0.1),      # Segundo byte, multiplicador 0.1
    "Gforce -(lateral)": (2, 0.01),  # Terceiro byte, multiplicador 0.01
    "Steering Angle (Placeholder)": (3, 1) # Quarto byte, multiplicador 1
}


# Cabeçalho do arquivo CSV. A ordem aqui define a ordem das colunas.
CSV_HEADER = [
    "Timestamp", "ECU RPM", "MAP", "TPS", "Engine temperature", "ECU Average O2",
    "ECU Injection Bank A Time", "ECU Batery voltage", "Oil pressure",
    "Fuel pressure", "Gear", "Brake pressure", "Traction speed",
    "Gforce -(lateral)", "Steering Angle (Placeholder)"
]

# =======================================================================
# 3. DADOS COMPARTILHADOS E SINCRONIZAÇÃO
# =======================================================================
# Dicionário para manter o estado mais recente dos sensores
telemetry_data = {sensor: "N/A" for sensor in CSV_HEADER}
# Trava para garantir que a leitura e escrita no dicionário sejam seguras
telemetry_lock = threading.Lock()

# =======================================================================
# 4. LÓGICA DO LEITOR E ARMAZENADOR CAN (Thread)
# =======================================================================
def process_value(raw_value, multiplier):
    """Aplica um multiplicador e retorna o valor processado."""
    return raw_value * multiplier

def process_standard_broadcast(msg, telemetry_dict):
    """Processa a mensagem CAN padrão da ECU."""
    try:
        # Extrai o ID da medição e o valor bruto do pacote CAN
        measure_id, raw_value = struct.unpack('>B f', msg.data)
        
        sensor_name = MEASURE_ID_MAP.get(measure_id)
        if sensor_name:
            # Atualiza o dicionário com o novo valor
            telemetry_dict[sensor_name] = raw_value
            # print(f"CAN Update: {sensor_name} = {raw_value}") # Descomente para debug
            
    except (struct.error, KeyError) as e:
        print(f"Erro ao processar pacote CAN padrão: {e}")

def process_simplified_packet(msg, telemetry_dict):
    """Processa a mensagem CAN simplificada de 4 bytes."""
    try:
        for sensor, (byte_index, multiplier) in SIMPLIFIED_PACKET_MAP.items():
            raw_value = msg.data[byte_index]
            processed_value = process_value(raw_value, multiplier)
            telemetry_dict[sensor] = processed_value
            # print(f"CAN Update: {sensor} = {processed_value}") # Descomente para debug
            
    except IndexError as e:
        print(f"Erro ao processar pacote CAN simplificado: {e}")

def can_reader_and_storage_thread():
    """
    Thread única que lê o CAN bus, atualiza o dicionário de telemetria
    e salva os dados em um arquivo CSV a cada atualização.
    """
    print(f"[CAN/Storage] Tentando inicializar a interface CAN '{CAN_INTERFACE}'...")
    try:
        bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan')
        print("[CAN/Storage] Interface CAN iniciada com sucesso.")
    except Exception as e:
        print(f"ERRO CRÍTICO: Não foi possível iniciar a interface CAN. {e}")
        print("Verifique se a interface está conectada e configurada corretamente.")
        return # Finaliza a thread se o CAN não funcionar

    # Garante que o arquivo CSV tenha um cabeçalho
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)
            print(f"[CAN/Storage] Arquivo '{DATA_FILE}' criado com cabeçalho.")
            
    print("[CAN/Storage] Lendo dados do CAN e armazenando...")
    while True:
        try:
            message = bus.recv(timeout=1.0) # Espera por uma mensagem por até 1 segundo
            if message is None:
                continue

            local_telemetry_copy = {}
            data_updated = False
            
            # Trava para modificar o dicionário global
            with telemetry_lock:
                if message.arbitration_id == 0x100:
                    process_standard_broadcast(message, telemetry_data)
                    data_updated = True
                elif message.arbitration_id == 0x200:
                    process_simplified_packet(message, telemetry_data)
                    data_updated = True
                
                # Faz uma cópia dos dados atuais para salvar
                local_telemetry_copy = telemetry_data.copy()

            # Se algum dado foi atualizado, salva a linha completa no CSV
            if data_updated:
                # Prepara a linha para salvar, na ordem correta do cabeçalho
                row_to_save = [local_telemetry_copy.get(key, 'N/A') for key in CSV_HEADER]
                
                # Atualiza o timestamp para o momento da escrita
                row_to_save[0] = time.time()
                
                # Adiciona a nova linha de dados ao arquivo
                with open(DATA_FILE, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(row_to_save)

        except Exception as e:
            print(f"ERRO na thread de leitura/armazenamento: {e}")
            time.sleep(5)

# =======================================================================
# 5. EXECUÇÃO PRINCIPAL
# =======================================================================
if __name__ == '__main__':
    print("--- INICIANDO PROCESSO DE COLETA E ARMAZENAMENTO ---")
    
    # Inicia a thread que lê o CAN e salva no arquivo
    main_thread = threading.Thread(target=can_reader_and_storage_thread, daemon=True)
    main_thread.start()
    
    print("Thread de coleta e armazenamento iniciada.")
    print("O programa está rodando em segundo plano. Pressione Ctrl+C para sair.")
    
    try:
        # Mantém o script principal vivo para que a thread continue rodando
        while main_thread.is_alive():
            main_thread.join(timeout=1.0)
    except KeyboardInterrupt:
        print("\nSinal de interrupção recebido. Encerrando o programa...")
    finally:
        print("Programa encerrado.")