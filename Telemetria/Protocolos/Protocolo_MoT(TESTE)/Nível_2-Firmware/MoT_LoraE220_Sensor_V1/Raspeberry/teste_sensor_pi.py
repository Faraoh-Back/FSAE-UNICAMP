# Importa as bibliotecas necessárias. Trocamos RPi.GPIO por gpiozero
import serial
import time
from gpiozero import OutputDevice, InputDevice

print("--- Iniciando Script de Teste com a Biblioteca GPIOZERO ---")

# --- Constantes de Configuração (permanecem as mesmas) ---
SERIAL_PORT = "/dev/serial0"
BAUDRATE = 9600

# Pinos GPIO (gpiozero usa a numeração BCM por padrão)
PIN_M0 = 17
PIN_M1 = 18
PIN_AUX = 27

# --- Bloco principal com tratamento de exceções ---
try:
    # 1. Configuração dos Pinos (Setup) com gpiozero
    # Em vez de GPIO.setup(), criamos objetos para cada pino
    print(f"Configurando pino M0 (GPIO{PIN_M0}) como saída...")
    pin_m0 = OutputDevice(PIN_M0)
    
    print(f"Configurando pino M1 (GPIO{PIN_M1}) como saída...")
    pin_m1 = OutputDevice(PIN_M1)
    
    print(f"Configurando pino AUX (GPIO{PIN_AUX}) como entrada...")
    pin_aux = InputDevice(PIN_AUX)
    print("Pinos configurados com sucesso!")

    # 2. Coloca o módulo LoRa em modo normal (M0=LOW, M1=LOW)
    # Em vez de GPIO.output(), usamos os métodos .off() e .on()
    print("Colocando o módulo em modo de transmissão normal...")
    pin_m0.off()  # .off() é o mesmo que nível lógico BAIXO (LOW)
    pin_m1.off()
    time.sleep(0.1)

    # 3. Inicializa a comunicação serial (esta parte não muda)
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    print(f"Porta serial {SERIAL_PORT} aberta. Aguardando mensagens LoRa...")

    # 4. Loop de Leitura (esta parte não muda)
    while True:
        if ser.in_waiting > 0:
            msg = ser.readline().decode('utf-8', errors='ignore').strip()
            if msg: # Só imprime se a mensagem não for vazia
                print(f"Recebido --> {msg}")

except KeyboardInterrupt:
    print("\nPrograma interrompido pelo usuário.")

except Exception as e:
    print(f"\nOcorreu um erro inesperado: {e}")

finally:
    # 5. Limpeza (Cleanup)
    # A biblioteca gpiozero gerencia a limpeza dos pinos automaticamente!
    # Só precisamos fechar a porta serial.
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Porta serial fechada.")
    
    print("Script finalizado.")