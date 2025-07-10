import can
import serial
import struct
import time
import threading
from datetime import datetime

# --- CONFIGURAÇÕES ---
CAN_INTERFACE = 'can0'
# Altere para a porta serial correta que vai para o PC (geralmente ttyUSB0 ou ttyACM0)
SERIAL_PORT_PC = '/dev/ttyUSB0' 
SERIAL_BAUDRATE_PC = 115200
# Taxa de envio de dados para o PC (em segundos)
TAXA_ENVIO_SERIAL = 0.1  # Envia 10x por segundo

# --- MAPEAMENTO DE SENSORES E PROTOCOLO (EXTRAÍDO DO PDF) ---

# Ordem final dos sensores para a string de saída serial
OUTPUT_SENSORS_ORDER = [
    "RPM", "MAP", "Engine Temp", "Oil Pressure", "Fuel Pressure", "Baterry Tension",
    "Sterring", "G Force", "Wheel Speed", "TPS", "Break Temp", "Break Pressure",
    "Susp Pressure", "Susp Travel", "Gear Position", "Oil Temp", "Water Temp"
]

# Mapeia o DataID do PDF para o nome do sensor e seu multiplicador
# Extraído das páginas 12 a 20 do Protocol_FTCAN20_Public_R026.pdf
MEASURE_ID_MAP = {
    0x0042: {'name': 'RPM', 'multiplier': 1.0},
    0x0002: {'name': 'TPS', 'multiplier': 0.1},
    0x0001: {'name': 'TPS', 'multiplier': 0.1},
    0x0002: {'name': 'TPS', 'multiplier': 0.1},
    0x0004: {'name': 'MAP', 'multiplier': 0.001},
    0x0008: {'name': 'Engine Temp', 'multiplier': 0.1},
    0x000A: {'name': 'Oil Pressure', 'multiplier': 0.001},
    0x000C: {'name': 'Fuel Pressure', 'multiplier': 0.001},
    0x0012: {'name': 'Baterry Tension', 'multiplier': 0.01},
    0x0014: {'name': 'Wheel Speed', 'multiplier': 1.0}, # Usando "Traction Speed" como velocidade da roda
    0x02A2: {'name': 'Break Pressure', 'multiplier': 0.001},
    0x0118: {'name': 'Oil Temp', 'multiplier': 0.1},
    0x0010: {'name': 'ECU Launch Mode', 'multiplier': 1.0}, # Usado para decodificar a marcha
    0x0022: {'name': 'Gear', 'multiplier': 1.0},
    0x000e: {'name': 'Water Temp', 'multiplier': 0.1},
    # Adicionar outros sensores que possam aparecer no bus, mesmo que não na lista final
    # Exemplo: Temperatura da Água pode vir no ID 0x000E do standard, ou 0x0008 da ECU simplificado.
    # O código irá mapear para o nome correto no dicionário de telemetria.
}

# Mapeamento para os pacotes simplificados (página 24 do PDF)
SIMPLIFIED_PACKET_MAP = {
    0x0600: ['TPS', 'MAP', 'Air Temperature', 'Engine Temp'],
    0x0601: ['Oil Pressure', 'Fuel Pressure', 'Water Pressure', 'Gear'],
    0x0602: ['Exhaust O2', 'RPM', 'Oil Temperature', 'Pit Limit'],
    0x0608: ['Oil Temp', 'Transmission Temperature', 'Fuel Consumption', 'Break Pressure'],
}

# Dicionário para armazenar o último valor lido de cada sensor
telemetry_data = {sensor: 0.0 for sensor in OUTPUT_SENSORS_ORDER}
telemetry_lock = threading.Lock()

def decode_can_id(can_id):
    """Extrai ProductID, DataFieldID e MessageID do ID CAN de 29 bits."""
    message_id = can_id & 0x7FF
    data_field_id = (can_id >> 11) & 0x7
    product_id = (can_id >> 14) & 0x7FFF
    return product_id, data_field_id, message_id

def process_value(raw_value, multiplier):
    """Converte o valor bruto de 16 bits (signed) e aplica o multiplicador."""
    # O valor é um inteiro de 16 bits com sinal (signed short)
    value_signed = struct.unpack('>h', struct.pack('>H', raw_value))[0]
    return value_signed * multiplier

def can_reader_thread():
    """Thread que lê a bus CAN e atualiza o dicionário de telemetria."""
    global telemetry_data
    try:
        with can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan') as bus:
            print(f"Ouvindo a interface CAN '{CAN_INTERFACE}'...")
            for msg in bus:
                if msg.is_extended_id:
                    _, _, message_id = decode_can_id(msg.arbitration_id)
                    data = msg.data

                    # Decodificação do Pacote Simplificado (mais comum para telemetria básica)
                    if message_id in SIMPLIFIED_PACKET_MAP:
                        sensor_names = SIMPLIFIED_PACKET_MAP[message_id]
                        with telemetry_lock:
                            for i, sensor_name in enumerate(sensor_names):
                                # Cada valor tem 2 bytes (big-endian)
                                raw_value = int.from_bytes(data[i*2:i*2+2], 'big')
                                
                                # Encontra o multiplicador no mapa principal
                                matching_id = next((k for k, v in MEASURE_ID_MAP.items() if v['name'] == sensor_name), None)
                                if matching_id:
                                    multiplier = MEASURE_ID_MAP[matching_id].get('multiplier', 1.0)
                                    final_value = process_value(raw_value, multiplier)
                                    
                                    # Atualiza o valor se o sensor estiver na nossa lista de interesse
                                    if sensor_name in telemetry_data:
                                        telemetry_data[sensor_name] = final_value
                                    
                                    # Lógica especial para a Marcha
                                    if sensor_name == 'Gear':
                                        telemetry_data['Gear Position'] = final_value
                                    elif sensor_name == 'Oil Temperature':
                                        telemetry_data['Oil Temp'] = final_value
                                        

                    # Futuramente, pode-se adicionar a decodificação do pacote standard aqui
                    # (MessageID 0x0FF, 0x1FF, etc.)
    except Exception as e:
        print(f"ERRO na thread de leitura do CAN: {e}")
        print("Verifique se a interface CAN está configurada corretamente com 'sudo ip link ...'")


def serial_writer_thread():
    """Thread que periodicamente envia os dados de telemetria para o PC via serial."""
    global telemetry_data
    try:
        with serial.Serial(SERIAL_PORT_PC, SERIAL_BAUDRATE_PC) as ser_pc:
            print(f"Enviando dados para o PC via porta serial '{SERIAL_PORT_PC}'...")
            while True:
                with telemetry_lock:
                    # Cria uma cópia para não segurar o lock durante a formatação
                    current_data_copy = telemetry_data.copy()
                
                # Formata a string de saída na ordem correta
                output_values = [str(current_data_copy.get(sensor, 0.0)) for sensor in OUTPUT_SENSORS_ORDER]
                output_string = f"<{';'.join(output_values)}>\n"
                
                # Envia para o PC
                ser_pc.write(output_string.encode('utf-8'))
                
                # Aguarda para a próxima transmissão
                time.sleep(TAXA_ENVIO_SERIAL)

    except Exception as e:
        print(f"ERRO na thread de escrita serial: {e}")
        print("Verifique se o cabo USB-Serial está conectado e a porta está correta.")

if __name__ == '__main__':
    print("Iniciando script de pré-processamento CAN da Raspberry Pi...")
    
    # Inicia as duas threads
    reader = threading.Thread(target=can_reader_thread, daemon=True)
    writer = threading.Thread(target=serial_writer_thread, daemon=True)

    reader.start()
    writer.start()

    print("Threads de leitura CAN e escrita Serial iniciadas.")
    print("Pressione Ctrl+C para sair.")
    
    try:
        # Mantém o script principal rodando
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nSaindo do script...")