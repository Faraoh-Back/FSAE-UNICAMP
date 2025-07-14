# =======================================================================
# Sensor.py - Versão Final Corrigida (13/07/2025)
# Compatível com Raspberry Pi 5 e configurado para 915 MHz
# =======================================================================

# --- BIBLIOTECAS CORRIGIDAS ---
import serial
from gpiozero import OutputDevice, InputDevice # Biblioteca moderna para GPIO
import time

# =======================================================================
# Constantes e Variáveis Globais
# =======================================================================
TAXA_SERIAL = 9600
TAMANHO_PACOTE = 52
RSSI_DOWNLINK = 50 
RECEIVER_ID = 8
TRANSMITTER_ID = 10
MY_ID = 100 

# Pinos GPIO para controle do E220 (numeração BCM)
PIN_M0 = 17  
PIN_M1 = 25  
PIN_AUX = 27 

# A pinagem UART é gerenciada pela configuração do sistema (/dev/serial0)

PacoteDL = bytearray([0] * TAMANHO_PACOTE) # Downlink Packet (received)
PacoteUL = bytearray([0] * TAMANHO_PACOTE) # Uplink Packet (to be sent)
RSSI_dBm_DL = 0.0 # RSSI in dBm from received message
RSSI_DL = 0       # RSSI converted to Radiuino format
LQI_DL = 0        # Link Quality Indicator
contadorUL = 0    # Uplink counter for Transport layer

# =======================================================================
# Classe E220TTL (CORRIGIDA)
# =======================================================================

class E220TTL:
    # --- __init__ CORRIGIDO ---
    # Usa a porta '/dev/serial0' por padrão e inicializa os pinos com gpiozero
    def __init__(self, serial_port='/dev/serial0', baud_rate=9600):
        # 1. Inicializa cada pino como um objeto gpiozero
        self.pin_m0 = OutputDevice(PIN_M0)
        self.pin_m1 = OutputDevice(PIN_M1)
        self.pin_aux = InputDevice(PIN_AUX)
        
        # 2. A linha GPIO.setmode() não é mais necessária. gpiozero usa BCM por padrão.
        
        # 3. Configuração da comunicação serial (para RXD/TXD)
        self.ser = serial.Serial(serial_port, baud_rate, timeout=0.1)

    # --- set_mode CORRIGIDO ---
    # Usa os métodos .on() e .off() do gpiozero
    def set_mode(self, mode):
        """Define o modo de operação do módulo."""
        if mode == 0: # Modo de Transmissão Transparente
            self.pin_m0.off()  # Equivalente a GPIO.LOW
            self.pin_m1.off()
        elif mode == 1: # WOR Mode
            self.pin_m0.on()   # Equivalente a GPIO.HIGH
            self.pin_m1.off()
        elif mode == 2: # Power Saving Mode
            self.pin_m0.off()
            self.pin_m1.on()
        elif mode == 3: # Configuration Mode
            self.pin_m0.on()
            self.pin_m1.on()

        time.sleep(0.1) 

    def begin(self):
        """Inicializa a comunicação e define o modo padrão."""
        if self.ser.is_open:
            print("E220TTL: Comunicação serial iniciada.")
            self.set_mode(0)
        else:
            print("E220TTL: Falha ao abrir a porta serial.")

    # --- configure_lora CORRIGIDO ---
    # Implementa a configuração real para 915 MHz
    def configure_lora(self):
        """Configura os parâmetros do módulo LoRa E220 para 915 MHz."""
        print("E220TTL: Entrando no modo de configuração (Modo 3)...")
        self.set_mode(3) 

        config_packet = bytearray([
            0xC0,  # CABEÇALHO: Salvar configuração na memória ao desligar.
            0x00,  # ENDEREÇO_ALTO: Endereço do módulo (0x0000 = genérico).
            0x00,  # ENDEREÇO_BAIXO: Endereço do módulo.
            0x62,  # REG0: UART 9600bps, 8N1. Air Data Rate 2.4kbps.
            0x41,  # REG1: Byte do Canal -> 0x41 (65 dec) => 850 + 65 = 915 MHz.
            0x41   # REG2: Potência de transmissão 22dBm, RSSI ativado.
        ])

        print(f"E220TTL: Enviando pacote de configuração para operar em 915 MHz...")
        print(f"E220TTL: Pacote (hex): {config_packet.hex()}")
        
        self.ser.write(config_packet)
        time.sleep(0.2) 

        print("E220TTL: Configuração concluída. Retornando ao modo de transmissão (Modo 0).")
        self.set_mode(0)

    def available(self):
        """Verifica se há dados disponíveis para leitura na porta serial."""
        return self.ser.in_waiting > 0

    def receiveMessageRSSI(self):
        """Recebe mensagem e RSSI do módulo LoRa."""
        if self.available():
            received_data = self.ser.read(self.ser.in_waiting)
            rssi_value = 0 
            if len(received_data) > 0:
                rssi_value = received_data[-1] 
                received_data = received_data[:-1] 
            return received_data, rssi_value
        return b'', 0

    def sendMessage(self, data, size):
        """Envia dados via a porta serial."""
        self.ser.write(data)
        print(f"E220TTL: Enviando mensagem de {size} bytes via porta serial.")

    def read_and_print_configuration(self):
        """Lê e imprime a configuração atual do módulo LoRa."""
        print("Lendo a configuracao do modulo para verificacao...")
        self.set_mode(3) # Entra no modo de configuração

        # Comando para ler 6 bytes de configuração a partir do endereço 0
        read_cmd = bytearray([0xC1, 0x00, 0x06])
        self.ser.write(read_cmd)
        time.sleep(0.1)

        # Lê a resposta
        response = self.ser.read(10) # Lê até 10 bytes para garantir

        self.set_mode(0) # Retorna ao modo normal

        if len(response) >= 6:
            # Dicionários para "traduzir" os bytes
            air_rates = {0b010: "2.4kbps", 0b011: "4.8kbps"}
            power_levels = {0b00: "30dBm", 0b01: "27dBm", 0b10: "24dBm", 0b11: "21dBm"} # Atenção: Datasheet do E220-900M30S

            reg0 = response[3]
            reg1 = response[4]
            reg2 = response[5]

            air_rate_val = reg0 & 0b111
            uart_baud_val = (reg0 >> 3) & 0b111

            freq_chan = reg1
            freq_mhz = 850 + freq_chan # Para a série 900M

            rssi_enabled = "SIM" if (reg2 >> 7) & 1 else "NAO"
            power_val_str = "22dBm (Padrão)" # Aproximação baseada na biblioteca do ESP

            print("----------------------------------------")
            print("         PARAMETROS DO MODULO LORA (RASPBERRY PI)     ")
            print("----------------------------------------")
            print(f"Frequencia       : {freq_mhz} MHz (Canal: {freq_chan})")
            # O endereço não é lido com este comando simples, mas sabemos que é 0x0000
            print(f"Endereco         : 0000") 
            print(f"Baud Rate UART   : { {0b011: '9600bps'}.get(uart_baud_val, 'Desconhecido') }")
            print(f"Velocidade no Ar : { air_rates.get(air_rate_val, 'Desconhecido') }")
            print(f"Potencia         : {power_val_str}")
            print(f"RSSI Ativado     : {rssi_enabled}")
            print("----------------------------------------")
        else:
            print("Falha ao ler a configuracao do modulo do Pi.")

# =======================================================================
# O restante do código (Camadas de Rede) permanece o mesmo.
# =======================================================================
e220ttl = E220TTL(baud_rate=TAXA_SERIAL) 

# 1.CAMADA FÍSICA
def inicializa_lora():
    e220ttl.begin()

def Phy_initialize():
    print(f"Serial inicializada em {TAXA_SERIAL} bps.")
    inicializa_lora()
    e220ttl.configure_lora()

def Phy_dBm_to_Radiuino():
    global RSSI_DL, LQI_DL
    if RSSI_dBm_DL > -10.5: RSSI_DL, LQI_DL = 127, 1
    elif -10.5 >= RSSI_dBm_DL >= -74: RSSI_DL, LQI_DL = int((RSSI_dBm_DL + 74) * 2), 0
    elif RSSI_dBm_DL < -74: RSSI_DL, LQI_DL = int(((RSSI_dBm_DL + 74) * 2) + 256), 0

def Phy_radio_receive():
    global RSSI_dBm_DL, PacoteDL
    received_message, rssi_value = e220ttl.receiveMessageRSSI()

    # ================================================================
    #      BLOCO DE DEBUG PARA VER QUALQUER PACOTE RECEBIDO
    # ================================================================
    # Este 'if' executa sempre que qualquer dado (de qualquer tamanho) chegar
    if received_message:
        print("--- [Raspberry Pi] PACOTE BRUTO RECEBIDO (HEX): ---")
        # .hex(' ') é uma forma fácil em Python de formatar o bytearray
        print(received_message.hex(' '))
        print(f"--> Tamanho do pacote recebido: {len(received_message)} bytes")
        print("----------------------------------------------------")
    # ================================================================

    if len(received_message) == TAMANHO_PACOTE:
        if rssi_value != 0: RSSI_dBm_DL = rssi_value - 256
        else: RSSI_dBm_DL = 0
        #O PacoteDL deve ser preenchido com os dados recebidos
        PacoteDL = bytearray(received_message)
        print("\n--- Estatísticas de Recebimento (PHY) ---")
        print(f"RSSI: {RSSI_dBm_DL:.2f} dBm")
        print(f"Pacote Recebido (Tamanho): {len(PacoteDL)} bytes")
        Mac_radio_receive()

def Phy_radio_send():
    global PacoteUL, RSSI_DL
    Phy_dBm_to_Radiuino()
    if RSSI_DOWNLINK < len(PacoteUL): PacoteUL[RSSI_DOWNLINK] = RSSI_DL
    e220ttl.sendMessage(PacoteUL, TAMANHO_PACOTE)

# 2.CAMADA MAC
def Mac_initialize(): print("MAC: Camada inicializada.")
def Mac_radio_receive(): Net_radio_receive()
def Mac_radio_send(): Phy_radio_send()

# 3.NETWORK
def Net_initialize(): print("Rede: Camada inicializada.")
# Em Sensor.py
def Net_radio_receive():
    print(f"Rede: Pacote recebido. Verificando ID do destinatário... (Esperado: {MY_ID}, Recebido: {PacoteDL[RECEIVER_ID]})")
    if PacoteDL[RECEIVER_ID] == MY_ID: 
        print("Rede: ID correto! Encaminhando para a camada de transporte.")
        Transp_radio_receive()
    else: 
        print(f"Rede: Pacote descartado. Não é para o meu ID.")
def Net_radio_send():
    PacoteUL[RECEIVER_ID] = PacoteDL[TRANSMITTER_ID]
    PacoteUL[TRANSMITTER_ID] = MY_ID
    Mac_radio_send()

# 4.CAMADA DE TRANSPORTE
def Transp_initialize(): print("Transporte: Camada inicializada.")
def Transp_radio_receive(): App_radio_receive()
def Transp_radio_send():
    global contadorUL
    contadorUL += 1
    print("\n--- Estatísticas de Envio (TRANSP) ---")
    print(f"Contador de Uplink: {contadorUL}")
    Net_radio_send()

# 5.CAMADA DE APLICAÇÕES
def App_initialize(): print("Aplicação: Camada inicializada.")
def App_radio_receive():
    print("Aplicação: Pacote recebido. Iniciando resposta.")
    App_radio_send()
def App_radio_send(): Transp_radio_send()

# COLE ESTE NOVO MÉTODO DENTRO DA CLASSE E220TTL NO ARQUIVO Sensor.py



# =======================================================================
# EXECUÇÃO PRINCIPAL
# =======================================================================
def setup():
    """Inicializa todas as camadas de comunicação."""
    print("Executando setup...")
    Phy_initialize()
    Mac_initialize()
    Net_initialize()
    Transp_initialize()
    App_initialize()

    e220ttl.read_and_print_configuration()

def loop():
    """O loop principal do programa para receber dados reais."""
    Phy_radio_receive()

if __name__ == "__main__":
    try:
        setup()
        print("\nSetup concluído. O rádio está pronto para comunicação em 915 MHz.")
        print("Aguardando pacotes... (Para testar, envie um pacote de outro rádio LoRa)")
        
        # O loop principal para operação real.
        while True:
            loop()
            time.sleep(0.1) # Pequena pausa para não sobrecarregar o processador

    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")
    finally:
        # Garante que os pinos GPIO sejam limpos ao sair
        # (gpiozero faz isso automaticamente, mas é uma boa prática)
        print("Limpando recursos e finalizando.")