import serial
import time
from gpiozero import OutputDevice, InputDevice

print("--- Iniciando Script LoRa (Raspberry Pi) ---")

# --- Constantes ---
SERIAL_PORT = "/dev/serial0"
BAUDRATE = 9600
PIN_M0 = 17
PIN_M1 = 18 
PIN_AUX = 27

# --- Funções ---
def set_lora_mode(mode, pin_m0, pin_m1):
    """Define o modo de operação do módulo LoRa."""
    if mode == 0:  # Modo Normal
        pin_m0.off()
        pin_m1.off()
        print("LoRa em MODO NORMAL.")
    elif mode == 2:  # Modo Configuração
        pin_m0.off()
        pin_m1.on()  # M1=HIGH, M0=LOW para configurar
        print("LoRa em MODO CONFIGURACAO.")

def configure_module(ser, pin_m0, pin_m1):
    """Envia o pacote de configuração para o módulo LoRa."""
    print("\n--- CONFIGURANDO MODULO LORA (Raspberry Pi) ---")
    
    # 1. Entra no modo de configuração
    set_lora_mode(2, pin_m0, pin_m1)
    time.sleep(0.5)

    # 2. Monta o EXATO MESMO pacote de configuração do ESP8266
    config_packet = bytearray([
        0xC0, 0x00, 0x06, 0x00, 0x00, 0x00, 0x62, 0x00, 0x41
    ])

    # 3. Envia o pacote de configuração
    ser.write(config_packet)
    print(f"Pacote de configuracao enviado: {config_packet.hex()}")
    time.sleep(0.5)

    # 4. Volta para o modo normal
    set_lora_mode(0, pin_m0, pin_m1)
    time.sleep(0.5)
    
    print("--- CONFIGURACAO CONCLUIDA ---")


# --- Bloco Principal ---
try:
    # 1. Inicializa os pinos GPIO
    pin_m0 = OutputDevice(PIN_M0)
    pin_m1 = OutputDevice(PIN_M1)
    pin_aux = InputDevice(PIN_AUX)
    print("Pinos GPIO configurados com sucesso!")

    # 2. Inicializa a comunicação serial
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    
    # 3. CHAMA A FUNÇÃO DE CONFIGURAÇÃO
    configure_module(ser, pin_m0, pin_m1)

    print(f"\nPronto. Aguardando mensagens LoRa na porta {SERIAL_PORT}...")

    # 4. Loop de Leitura
    while True:
        if ser.in_waiting > 0:
            # .read() é melhor que .readline() para dados brutos
            msg_bytes = ser.read(ser.in_waiting)
            try:
                msg_str = msg_bytes.decode('utf-8', errors='ignore').strip()
                if msg_str:
                    print(f"Recebido --> '{msg_str}'")
            except Exception as e:
                print(f"Erro ao decodificar mensagem: {e}")

except KeyboardInterrupt:
    print("\nPrograma interrompido pelo usuário.")
except Exception as e:
    print(f"\nOcorreu um erro inesperado: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Porta serial fechada.")
    print("Script finalizado.")