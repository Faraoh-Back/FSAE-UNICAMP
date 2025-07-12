#include "Bibliotecas.h"

// Protótipos das Funções
void inicializa_lora();
void enviarComandoParaSensor();
void receberRespostaDoSensor();
void enviarDadosParaPC();
void converterRSSI(int rssi_dbm);

void setup() {
  Serial.begin(TAXA_SERIAL);
  while (!Serial);
  
  inicializa_lora();
  Serial.println("\n--- Base LoRa (ESP8266) Pronta ---");
}

void loop() {
  // A cada X segundos, envia um comando para o sensor
  if (millis() - ultimoPoll >= INTERVALO_POLL) {
    ultimoPoll = millis(); // Reseta o timer
    enviarComandoParaSensor();
  }
  
  // Ouve continuamente por uma resposta do sensor
  receberRespostaDoSensor();
}

void inicializa_lora() {
  loraSerial.begin(9600);
  e22ttl.begin();

  // Lê a configuração atual do módulo
  ResponseStructContainer c;
  c = e22ttl.getConfiguration();
  Configuration configuration = *(Configuration*) c.data;
  
  // Modifica os parâmetros desejados
  configuration.ADDL = MY_ID;
  configuration.CHAN = CANAL_LORA;
  
  configuration.SPED.uartBaudRate = UART_BPS_9600;
  configuration.SPED.airDataRate = AIR_DATA_RATE_010_24; // 2.4kbps
  
  configuration.OPTION.transmissionPower = POWER_22;
  
  configuration.TRANSMISSION_MODE.fixedTransmission = FT_FIXED_TRANSMISSION;
  configuration.TRANSMISSION_MODE.enableRSSI = RSSI_ENABLED;

  // Grava a nova configuração no módulo
  ResponseStatus rs = e22ttl.setConfiguration(configuration, WRITE_CFG_PWR_DWN_SAVE);
  if (rs.code != E22_SUCCESS) {
    Serial.println("Erro ao salvar configuracao!");
    while(1);
  }
  
  Serial.println("Modulo LoRa da Base configurado.");
  delete (Configuration*)c.data;
}

void enviarComandoParaSensor() {
  Serial.print("Enviando comando para o Sensor ID: ");
  Serial.println(ID_DO_SENSOR);

  // Prepara um pacote de comando simples
  memset(PacoteDL, 0, TAMANHO_PACOTE); // Limpa o pacote com zeros
  PacoteDL[RECEIVER_ID] = ID_DO_SENSOR;
  PacoteDL[TRANSMITTER_ID] = MY_ID;

  e22ttl.sendFixedMessage(0, ID_DO_SENSOR, CANAL_LORA, PacoteDL, TAMANHO_PACOTE);
}

void receberRespostaDoSensor() {
  if (e22ttl.available() > 1) { 
    ResponseContainer rc = e22ttl.receiveMessageRSSI();
    
    if (rc.status.code == E22_SUCCESS) {
      if (rc.data.length() >= TAMANHO_PACOTE) {
        memcpy(PacoteUL, rc.data.c_str(), TAMANHO_PACOTE);
        
        if (PacoteUL[TRANSMITTER_ID] == ID_DO_SENSOR && PacoteUL[RECEIVER_ID] == MY_ID) {
          Serial.print("Resposta recebida do Sensor! RSSI: ");
          Serial.println(rc.rssi);
          
          RSSI_dBm_UL = rc.rssi;
          enviarDadosParaPC();
        }
      }
    }
  }
}

void enviarDadosParaPC() {
  converterRSSI(RSSI_dBm_UL);
  PacoteUL[RSSI_UPLINK] = RSSI_UL;
  PacoteUL[LQI_UPLINK] = LQI_UL;

  Serial.write(PacoteUL, TAMANHO_PACOTE);
  Serial.flush();
  Serial.println("\nDados do sensor enviados para o PC.");
}

void converterRSSI(int rssi_dbm) {
  if (rssi_dbm > -10.5) {
   RSSI_UL = 127; LQI_UL = 1;
  } else if (rssi_dbm <= -10.5 && rssi_dbm >= -74) {
   RSSI_UL = ((rssi_dbm + 74) * 2); LQI_UL = 0;
  } else {
   RSSI_UL = (((rssi_dbm + 74) * 2) + 256); LQI_UL = 0;
  }
}