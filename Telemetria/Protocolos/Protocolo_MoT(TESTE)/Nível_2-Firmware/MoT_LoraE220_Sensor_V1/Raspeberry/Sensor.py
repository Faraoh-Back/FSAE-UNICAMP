# Sensor.py (Corrigido para Raspberry Pi)

import serial
import RPi.GPIO as GPIO
import time


# =======================================================================
# Constantes e Variáveis Globais
# =======================================================================
TAXA_SERIAL = 9600
TAMANHO_PACOTE = 52
RSSI_DOWNLINK = 50 
RECEIVER_ID = 0
TRANSMITTER_ID = 1
MY_ID = 100 

# Pinos GPIO para controle do E220 (BCM numbering)
# Certifique-se de que estes pinos correspondem às suas conexões físicas
PIN_M0 = 17  
PIN_M1 = 25  
PIN_AUX = 27 

# Pinagem UART (Padrão Raspberry Pi 5)
# TXD: GPIO14 (/dev/ttyS0)
# RXD: GPIO15 (/dev/ttyS0)

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
        self.ser = serial.Serial(serial_port, baud_rate, timeout=0.1)

    def set_mode(self, mode):
        """Define o modo de operação do módulo."""
        # Configura os pinos M0 e M1 para o modo especificado
        if mode == 0: # Modo de Transmissão Transparente (Mode 0)
            GPIO.output(PIN_M0, GPIO.LOW)
            GPIO.output(PIN_M1, GPIO.LOW)
        elif mode == 1: # WOR Mode (Wake On Radio)
            GPIO.output(PIN_M0, GPIO.HIGH)
            GPIO.output(PIN_M1, GPIO.LOW)
        elif mode == 2: # Power Saving Mode
            GPIO.output(PIN_M0, GPIO.LOW)
            GPIO.output(PIN_M1, GPIO.HIGH)
        elif mode == 3: # Configuration Mode (Deep Sleep)
            GPIO.output(PIN_M0, GPIO.HIGH)
            GPIO.output(PIN_M1, GPIO.HIGH)
        
        # Wait for module to stabilize after mode change (recommended by datasheet)
        time.sleep(0.1) 

    def begin(self):
        """Inicializa a comunicação e define o modo padrão."""
        if self.ser.is_open:
            print("E220TTL: Serial communication started.")
            self.set_mode(0) # Define o modo de operação padrão para transmissão
        else:
            print("E220TTL: Failed to open serial port.")

    def configure_lora(self):
        """Configures the LoRa E220 module parameters."""
        print("E220TTL: Entering configuration mode (Mode 3)...")
        self.set_mode(3) 

        # --- AVISO: Configuração de Frequência e Parâmetros ---
        # A frequência e os parâmetros são definidos enviando bytes de configuração 
        # específicos para o módulo E220-900T30D. Você precisa consultar o datasheet 
        # do módulo para obter os bytes corretos para 915 MHz e outras configurações 
        # (ex: Air Data Rate, Power TX).

        # Exemplo de pacote de configuração (você DEVE substituir com os bytes corretos):
        # C0 (Header), ADDH (Address High), ADDL (Address Low), 
        # SPED (UART rate, Air data rate), CHAN (Channel frequency), OPTION (Power, RSSI, etc.)
        
        # O E220-900T30D opera de 850.125MHz a 930.125MHz. 
        
        # Para 915 MHz, você deve calcular o byte CHAN apropriado e enviar o pacote completo.
        # Ex: bytearray([0xC0, 0x00, 0x00, 0x1A, 0x5B, 0x44]) # Placeholder example config
        
        # self.ser.write(config_packet)
        # time.sleep(0.1) # Espera o módulo processar a configuração

        print("E220TTL: Configuration complete. Returning to transparent transmission (Mode 0).")
        self.set_mode(0) # Retorna ao modo de transmissão transparente

    def available(self):
        """Verifica se há dados disponíveis para leitura na porta serial."""
        return self.ser.in_waiting > 0

    def receiveMessageRSSI(self):
        """Recebe mensagem e RSSI do módulo LoRa."""
        if self.available():
            # A E220 envia o RSSI no final do pacote (se configurado)
            received_data = self.ser.read(self.ser.in_waiting)
            
            # Placeholder para RSSI, se não for extraído do pacote
            rssi_value = 0 
            
            # Se o último byte do pacote for o RSSI (e o RSSI esteja habilitado na config do módulo)
            if len(received_data) > 0:
                # O RSSI é geralmente o último byte recebido.
                rssi_value = received_data[-1] 
                received_data = received_data[:-1] # Remove o RSSI do pacote de dados

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
    e220ttl.configure_lora() # Chama a função de configuração para 915 MHz

def Phy_dBm_to_Radiuino():
    """Converts RSSI (dBm) to the Radiuino format."""
    global RSSI_DL, LQI_DL

    # Assegurar que RSSI_dBm_DL é um valor válido antes de converter
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

    # Verifica se há dados disponíveis antes de tentar ler
    received_message, rssi_value = e220ttl.receiveMessageRSSI()
    
    if len(received_message) == TAMANHO_PACOTE - 1: # -1 porque removemos o RSSI do pacote
        # A conversão de RSSI do E220 (0-255) para dBm depende da configuração. 
        # Se o RSSI for o último byte, 
        # RSSI (dBm) = RSSI_Value - 256 (Ebyte specific conversion)
        
        # A linha original no código era: RSSI_dBm_DL = -1 * (256 - rssi_value)
        
        # Se o RSSI for 0, significa que não foi extraído corretamente (como no placeholder original)
        if rssi_value != 0:
            RSSI_dBm_DL = rssi_value - 256
        else:
            RSSI_dBm_DL = 0 # Valor padrão se não houver RSSI válido

        PacoteDL = bytearray(received_message)

        # Preenche o PacoteUL com dados de exemplo para responder (se necessário)
        for i in range(TAMANHO_PACOTE):
            PacoteUL[i] = i % 256 # Exemplo de dados: 0, 1, 2, ...

        # Prints de Estatísticas de Recebimento
        print("\n--- Estatísticas de Recebimento (PHY) ---")
        print(f"RSSI (dBm): {RSSI_dBm_DL:.2f} dBm")
        print(f"Pacote Recebido (Tamanho): {len(PacoteDL)} bytes")
        print(f"Pacote Recebido (Conteúdo): {PacoteDL.hex()}")
        print("-----------------------------------------")
        
        # Se o pacote foi recebido com sucesso, passa para a camada MAC
        Mac_radio_receive()

def Phy_radio_send():
    """Sends data via the radio."""
    global PacoteUL, RSSI_DL

    Phy_dBm_to_Radiuino()
    
    # Adiciona o RSSI convertido ao pacote de uplink (se houver um campo para isso)
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
    else:
        print(f"Net_radio_receive: Packet not addressed to MY_ID ({MY_ID}). Packet receiver ID: {PacoteDL[RECEIVER_ID]}")

def Net_radio_send():
    """Prepares and sends packet to the MAC layer."""
    # Define o ID do receptor como o ID do transmissor do pacote recebido
    PacoteUL[RECEIVER_ID] = PacoteDL[TRANSMITTER_ID]
    # Define o ID do transmissor como o ID desta estação
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
    
    # A ordem de inicialização é importante.
    Phy_initialize() # Configura o LoRa e a serial, e o modo de operação
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
    
    # Simulação de um pacote recebido para testar o fluxo de downlink
    # e acionar o fluxo de uplink (resposta).
    # O PacoteDL deve ter MY_ID como RECEIVER_ID para ser processado.
    PacoteDL[RECEIVER_ID] = MY_ID  
    PacoteDL[TRANSMITTER_ID] = 50   
    
    print("\nSimulating reception flow by manually calling Mac_radio_receive():")
    # Chama a função MAC receive para simular a chegada de um pacote 
    # (aqui, usando o pacote DL preenchido manualmente acima)
    Mac_radio_receive()

    # O loop() seria executado continuamente em um ambiente real
    # while True:
    #     loop()