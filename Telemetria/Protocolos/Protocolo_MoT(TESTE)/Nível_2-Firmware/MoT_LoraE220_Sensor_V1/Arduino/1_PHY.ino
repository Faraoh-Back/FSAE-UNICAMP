import time

TAXA_SERIAL = 9600
TAMANHO_PACOTE = 52
FREQUENCY_IN_MHZ = 433.0
POWER_TX_DBM = 20
RSSI_DOWNLINK = 50 

PacoteDL = bytearray(TAMANHO_PACOTE)
PacoteUL = bytearray(TAMANHO_PACOTE)
RSSI_dBm_DL = 0
RSSI_DL = 0
LQI_DL = 0


class E220TTL:
    def begin(self):
        print("E220TTL: Initializing UART and pins.")

    def available(self):
        return False

    def receiveMessageRSSI(self):

        class ResponseContainer:
            def __init__(self, data, rssi):
                self.data = data
                self.rssi = rssi
        return ResponseContainer(b'', 0)

    def sendMessage(self, data, size):
        print(f"E220TTL: Sending message of size {size}")
        print(f"Data: {data.hex()}")


e220ttl = E220TTL()


def inicializa_lora():
    """Initializes the LoRa module (simulated)."""

    e220ttl.begin()


def Phy_initialize():
    """Physical layer initialization function."""

    inicializa_lora()
    print("Phy_initialize: Physical layer initialized.")

def Mac_radio_receive():
    """Placeholder for the MAC layer receive function."""
    print("Mac_radio_receive: Handing packet to MAC layer.")
    
def Phy_radio_receive():
    """Receives data from the radio."""
    global RSSI_dBm_DL, PacoteDL, PacoteUL

    if e220ttl.available():
        rc = e220ttl.receiveMessageRSSI()
        rssi_value = rc.rssi
        received_message = rc.data
        

        if len(received_message) == TAMANHO_PACOTE:

            RSSI_dBm_DL = -1 * (256 - rssi_value)


            PacoteDL = bytearray(received_message)


            for i in range(TAMANHO_PACOTE):
                PacoteUL[i] = 1


            Mac_radio_receive()
        else:
            print(f"Phy_radio_receive: Received packet of invalid size: {len(received_message)}")

def Phy_dBm_to_Radiuino():
    """
    Converts RSSI in dBm to the Radiuino format (complement of 2, step 1/2, offset 74).
    """
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
    


def Phy_radio_send():
    """Sends data via the radio."""
    global PacoteUL, RSSI_DL

    Phy_dBm_to_Radiuino()
    

    if RSSI_DOWNLINK < len(PacoteUL):
        PacoteUL[RSSI_DOWNLINK] = RSSI_DL
    else:
        print("Error: RSSI_DOWNLINK index out of bounds for PacoteUL.")


    e220ttl.sendMessage(PacoteUL, TAMANHO_PACOTE)


if __name__ == "__main__":
    print("Simulating Arduino Phy Layer behavior in Python.")
    
    Phy_initialize()
    

    RSSI_dBm_DL = -80.0
    Phy_dBm_to_Radiuino()
    print(f"\nExample RSSI Conversion:")
    print(f"Input RSSI (dBm): {RSSI_dBm_DL}")
    print(f"Converted RSSI_DL: {RSSI_DL}")
    print(f"LQI_DL: {LQI_DL}")
    

    PacoteUL = bytearray([i % 256 for i in range(TAMANHO_PACOTE)])
    
    print("\nSimulating radio send:")
    Phy_radio_send()