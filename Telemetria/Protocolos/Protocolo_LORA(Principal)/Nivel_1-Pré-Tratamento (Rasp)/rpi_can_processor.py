import can
import serial
import struct
import time
import threading
from datetime import datetime

# --- CONFIGURAÇÕES ---
CAN_INTERFACE = 'can0'
SERIAL_PORT_PC = '/dev/ttyUSB0'
SERIAL_BAUDRATE_PC = 115200
TAXA_ENVIO_SERIAL = 0.1

# --- MAPEAMENTO E FORMATAÇÃO DE SENSORES ---

OUTPUT_SENSORS_ORDER = [
    "ECU RPM", "MAP", "Engine temperature", "Oil pressure", "Fuel pressure",
    "ECU Batery voltage", "Steering Angle (Placeholder)", "Gforce -(lateral)",
    "Traction speed", "TPS", "Brake pressure", "Suspension Travel (Placeholder)",
    "Gear", "ECU Average O2", "ECU Injection Bank A Time"
]

# NOVO: Dicionário para controlar a precisão (casas decimais) de cada sensor na saída
SENSOR_PRECISION = {
    "ECU RPM": 0,
    "MAP": 2,
    "Engine temperature": 1,
    "Oil pressure": 1,
    "Fuel pressure": 1,
    "ECU Batery voltage": 2,
    "Steering Angle (Placeholder)": 2,
    "Gforce -(lateral)": 1,
    "Traction speed": 1,
    "TPS": 2,
    "Brake pressure": 1,
    "Suspension Travel (Placeholder)": 2,
    "Gear": 0,
    "ECU Average O2": 3,
    "ECU Injection Bank A Time": 2
}

MEASURE_ID_MAP = {
    0x0084: {'name': 'ECU RPM', 'multiplier': 1.0},
    0x0004: {'name': 'MAP', 'multiplier': 0.001},
    0x0008: {'name': 'Engine temperature', 'multiplier': 0.1},
    0x000A: {'name': 'Oil pressure', 'multiplier': 0.001},
    0x000C: {'name': 'Fuel pressure', 'multiplier': 0.001},
    0x0012: {'name': 'ECU Batery voltage', 'multiplier': 0.01},
    0x0014: {'name': 'Traction speed', 'multiplier': 1.0},
    0x0002: {'name': 'TPS', 'multiplier': 0.1},
    0x02A2: {'name': 'Brake pressure', 'multiplier': 0.001},
    0x0022: {'name': 'Gear', 'multiplier': 1.0},
    0x00A2: {'name': 'ECU Average O2', 'multiplier': 0.001},
    0x0086: {'name': 'ECU Injection Bank A Time', 'multiplier': 0.01},
    # Adicionado para Força G dos pacotes simplificados
    0x0040: {'name': 'Gforce -(lateral)', 'multiplier': 0.001}, # Multiplicador hipotético
}

SIMPLIFIED_PACKET_MAP = {
    0x0600: ['TPS', 'MAP', 'Air Temperature', 'Engine temperature'],
    0x0601: ['Oil pressure', 'Fuel pressure', 'Water Pressure', 'Gear'],
    0x0602: ['ECU Average O2', 'ECU RPM', 'Oil Temperature', 'Pit Limit'],
    0x0606: ['Gforce -(accel)', 'Gforce -(lateral)', 'Yaw-rate (frontal)', 'Yaw-rate (lateral)'],
    0x0608: ['Oil Temperature', 'Transmission Temperature', 'Fuel Consumption', 'Brake pressure'],
}

telemetry_data = {sensor: 0.0 for sensor in OUTPUT_SENSORS_ORDER}
telemetry_lock = threading.Lock()

def process_value(raw_value, multiplier):
    value_signed = struct.unpack('>h', struct.pack('>H', raw_value))[0]
    return value_signed * multiplier

def update_telemetry_data(sensor_name, value):
    with telemetry_lock:
        if sensor_name in telemetry_data:
            telemetry_data[sensor_name] = value

def process_standard_broadcast(msg):
    for i in range(0, msg.dlc, 4):
        measure_id = int.from_bytes(msg.data[i:i+2], 'big')
        raw_value = int.from_bytes(msg.data[i+2:i+4], 'big')
        if measure_id in MEASURE_ID_MAP:
            sensor_info = MEASURE_ID_MAP[measure_id]
            final_value = process_value(raw_value, sensor_info['multiplier'])
            update_telemetry_data(sensor_info['name'], final_value)

def process_simplified_packet(msg):
    sensor_names_from_can = SIMPLIFIED_PACKET_MAP[msg.arbitration_id & 0x7FF]
    for i, sensor_name_can in enumerate(sensor_names_from_can):
        raw_value = int.from_bytes(msg.data[i*2:i*2+2], 'big')
        matching_id = next((k for k, v in MEASURE_ID_MAP.items() if v['name'] == sensor_name_can), None)
        multiplier = 1.0
        if matching_id:
            multiplier = MEASURE_ID_MAP[matching_id].get('multiplier', 1.0)
        final_value = process_value(raw_value, multiplier)
        update_telemetry_data(sensor_name_can, final_value)

def can_reader_thread():
    try:
        with can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan') as bus:
            print(f"Ouvindo a interface CAN '{CAN_INTERFACE}'...")
            for msg in bus:
                if not msg.is_extended_id: continue
                message_id = msg.arbitration_id & 0x7FF
                if 0x0FF <= message_id <= 0x3FF:
                    process_standard_broadcast(msg)
                elif message_id in SIMPLIFIED_PACKET_MAP:
                    process_simplified_packet(msg)
    except Exception as e:
        print(f"ERRO na thread de leitura do CAN: {e}")

def serial_writer_thread():
    try:
        with serial.Serial(SERIAL_PORT_PC, SERIAL_BAUDRATE_PC) as ser_pc:
            print(f"Enviando dados para o PC via porta serial '{SERIAL_PORT_PC}'...")
            while True:
                with telemetry_lock:
                    current_data_copy = telemetry_data.copy()

                # --- ALTERADO: Loop para formatar cada valor com sua precisão específica ---
                output_values = []
                for sensor in OUTPUT_SENSORS_ORDER:
                    value = current_data_copy.get(sensor, 0.0)
                    precision = SENSOR_PRECISION.get(sensor, 2)  # Usa 2 como padrão
                    output_values.append(f"{value:.{precision}f}")
                
                output_string = f"<{';'.join(output_values)}>\n"
                ser_pc.write(output_string.encode('utf-8'))
                time.sleep(TAXA_ENVIO_SERIAL)
    except Exception as e:
        print(f"ERRO na thread de escrita serial: {e}")

if __name__ == '__main__':
    print("Iniciando script de pré-processamento CAN da Raspberry Pi (Versão Final)...")
    reader = threading.Thread(target=can_reader_thread, daemon=True)
    writer = threading.Thread(target=serial_writer_thread, daemon=True)
    reader.start()
    writer.start()
    print("Pressione Ctrl+C para sair.")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\nSaindo...")
