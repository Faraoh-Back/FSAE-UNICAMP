# Sensor.py (Modificado para Raspberry Pi)

import serial
import RPi.GPIO as GPIO
import time
import struct

# =======================================================================
# Constantes e Variáveis Globais
# =======================================================================
TAXA_SERIAL = 9600
TAMANHO_PACOTE = 52
RSSI_DOWNLINK = 50 
RECEIVER_ID = 0
TRANSMITTER_ID = 1
MY_ID = 100 

# Pinos GPIO para controle do E220 (baseado na tabela de conexões fornecida)
# M0 (Pino 11 / GPIO17)
# M1 (Pino 22 / GPIO25)
# AUX (Pino 13 / GPIO27)
PIN_M0 = 17  
PIN_M1 = 25  
PIN_AUX = 27 


PacoteDL = bytearray([0] * TAMANHO_PACOTE) # Downlink Packet (received)
PacoteUL = bytearray([0] * TAMANHO_PACOTE) # Uplink Packet (to be sent)
RSSI_dBm_DL = 0.0 # RSSI in dBm from received message
RSSI_DL = 0       # RSSI converted to Radiuino format
LQI_DL = 0        # Link Quality Indicator
contadorUL = 0    # Uplink counter for Transport layer

# =======================================================================
# Classe E220TTL
# =======================================================================

class E220TTL:
    def __init__(self, serial_port='/dev/ttyS0', baud_rate=9600):
        # Configuração inicial dos pinos GPIO (para M0, M1 e AUX)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([PIN_M0, PIN_M1], GPIO.OUT)
        GPIO.setup(PIN_AUX, GPIO.IN)
        
        # Configuração da comunicação serial (para RXD/TXD)
        # /dev/ttyS0 é a porta UART padrão da Raspberry Pi
        self.ser = serial.Serial(serial_port, baud_rate, timeout=0.1)

    def set_mode(self, mode):
        """Define o modo de operação do módulo."""
        # Configura os pinos M0 e M1 para o modo especificado
        if mode == 0: # Modo de Transmissão Transparente
            GPIO.output(PIN_M0, GPIO.LOW)
            GPIO.output(PIN_M1, GPIO.LOW)
        time.sleep(0.1) 

    def begin(self):
        """Inicializa a comunicação e define o modo padrão."""
        if self.ser.is_open:
            print("E220TTL: Serial communication started.")
            self.set_mode(0) # Define o modo de operação padrão para transmissão
        else:
            print("E220TTL: Failed to open serial port.")

    def available(self):
        """Verifica se há dados disponíveis para leitura na porta serial."""
        return self.ser.in_waiting > 0

    def receiveMessageRSSI(self):
        """Recebe mensagem e RSSI do módulo LoRa."""
        if self.available():
            received_data = self.ser.read(self.ser.in_waiting)
            rssi_value = 0 # Placeholder para RSSI, se não for extraído do pacote
            return received_data, rssi_value
        return b'', 0

    def sendMessage(self, data, size):
        """Envia dados via a porta serial."""
        self.ser.write(data)
        print(f"E220TTL: Sending message of size {size} via real serial.")

e220ttl = E220TTL(baud_rate=TAXA_SERIAL) 

# =======================================================================
# 1.CAMADA FÍSICA
# =======================================================================

def inicializa_lora():
    """Initializes the LoRa module (E220 TTL)."""
    e220ttl.begin()

def Phy_initialize():
    """Physical layer initialization."""
    print(f"Serial initialized at {TAXA_SERIAL}.")
    inicializa_lora()

def Phy_dBm_to_Radiuino():
    """Converts RSSI (dBm) to the Radiuino format."""
    global RSSI_DL, LQI_DL

    if RSSI_dBm_DL > -10.5:
        RSSI_DL = 127 
        LQI_DL = 1 
    elif -10.5 >= RSSI_dBm_DL >= -74:
        RSSI_DL = int((RSSI_dBm_DL + 74) * 2)
        LQI_DL = 0
    elif RSSI_dBm_DL < -74:
        RSSI_DL = int(((RSSI_dBm_DL + 74) * 2) + 256)
        LQI_DL = 0

def Phy_radio_receive():
    """Receives data from the radio."""
    global RSSI_dBm_DL, PacoteDL, PacoteUL

    if e220ttl.available():
        rc = e220ttl.receiveMessageRSSI()
        rssi_value = rc[1] 
        received_message = rc[0] 
        
        if len(received_message) == TAMANHO_PACOTE:
            RSSI_dBm_DL = -1 * (256 - rssi_value) 
            PacoteDL = bytearray(received_message)

            for i in range(TAMANHO_PACOTE):
                PacoteUL[i] = 1

            # Prints de Estatísticas de Recebimento
            print("\n--- Estatísticas de Recebimento (PHY) ---")
            print(f"RSSI (dBm): {RSSI_dBm_DL:.2f} dBm")
            print(f"Pacote Recebido (Tamanho): {len(PacoteDL)} bytes")
            print(f"Pacote Recebido (Conteúdo): {PacoteDL.hex()}")
            print("-----------------------------------------")
            
            Mac_radio_receive()

def Phy_radio_send():
    """Sends data via the radio."""
    global PacoteUL, RSSI_DL

    Phy_dBm_to_Radiuino()
    
    if RSSI_DOWNLINK < len(PacoteUL):
        PacoteUL[RSSI_DOWNLINK] = RSSI_DL
    
    e220ttl.sendMessage(PacoteUL, TAMANHO_PACOTE)

# =======================================================================
# 2.CAMADA MAC
# =======================================================================

def Mac_initialize():
    """Initializes the Medium Access Control (MAC) layer. (Currently empty)"""
    print("Mac_initialize: MAC layer initialized.")

def Mac_radio_receive():
    """Receives packet from the Physical layer and passes it to the Network layer."""
    Net_radio_receive()

def Mac_radio_send():
    """Sends packet to the Physical layer."""
    Phy_radio_send()

# =======================================================================
# 3.NETWORK
# =======================================================================

def Net_initialize():
    """Initializes the Network layer. (Currently empty)"""
    print("Net_initialize: Network layer initialized.")

def Net_radio_receive():
    """Receives packet from the MAC layer and checks if it is addressed to this device (MY_ID)."""
    if PacoteDL[RECEIVER_ID] == MY_ID:
        Transp_radio_receive()

def Net_radio_send():
    """Prepares and sends packet to the MAC layer."""
    PacoteUL[RECEIVER_ID] = PacoteDL[TRANSMITTER_ID]
    PacoteUL[TRANSMITTER_ID] = MY_ID
    
    Mac_radio_send()

# =======================================================================
# 4.CAMADA DE TRANSPORTE
# =======================================================================

def Transp_initialize():
    """Initializes the Transport layer. (Currently empty)"""
    print("Transp_initialize: Transport layer initialized.")

def Transp_radio_receive():
    """Receives packet from the Network layer and passes it to the Application layer."""
    App_radio_receive()

def Transp_radio_send():
    """Increments the uplink counter and sends the packet to the Network layer."""
    global contadorUL
    contadorUL += 1
    
    # Prints de Estatísticas de Envio (TRANSP)
    print("\n--- Estatísticas de Envio (TRANSP) ---")
    print(f"Contador de Uplink (Pacotes Enviados): {contadorUL}")
    print(f"Pacote de Uplink (Tamanho): {len(PacoteUL)} bytes")
    print("---------------------------------------")
    
    Net_radio_send()

# =======================================================================
# 5.CAMADA DE APLICAÇÕES
# =======================================================================

def App_initialize():
    """Initializes the Application layer. (Currently empty)"""
    print("App_initialize: Application layer initialized.")

def App_radio_receive():
    """Receives data and triggers a response send."""
    print("App_radio_receive: Packet received. Initiating response.")
    App_radio_send()

def App_radio_send():
    """Sends data from the Application layer to the Transport layer."""
    Transp_radio_send()

# =======================================================================
# MoT_LoraE220_Sensor_V1
# =======================================================================

def setup():
    """Initializes all communication layers."""
    print("Executing setup...")
    Phy_initialize()
    Mac_initialize()
    Net_initialize()
    Transp_initialize()
    App_initialize()

def loop():
    """The main loop of the program."""
    Phy_radio_receive()

# =======================================================================
# EXECUÇÃO
# =======================================================================
if __name__ == "__main__":
    setup()
    
    PacoteDL[RECEIVER_ID] = MY_ID  
    PacoteDL[TRANSMITTER_ID] = 50   
    
    print("\nSimulating reception flow by manually calling Mac_radio_receive():")
    Mac_radio_receive()