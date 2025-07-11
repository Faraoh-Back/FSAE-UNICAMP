/*
  MoT LoRa | WissTek IoT
  Adaptado para ESP8266 mantendo a estrutura original.
*/

//=======================================================================
//                     1 - Bibliotecas
//=======================================================================
#include "Bibliotecas.h"

// Protótipos das novas funções
void configura_lora();

//=======================================================================
//                     2 - Setup de inicialização
//=======================================================================
void setup() {
  Phy_initialize();
  Mac_initialize();
  Net_initialize();
  // Mensagem para indicar que a base está pronta
  Serial.println("\n--- Base LoRa (ESP8266) Pronta ---");
}

//=======================================================================
//                     3 - Loop de repetição
//=======================================================================
void loop() {
  Phy_serial_receive(); // Ouve comandos da borda (PC/Raspberry)
  Phy_radio_receive();  // Ouve pacotes do rádio (do sensor no carro)
}

//=======================================================================
//                 Camada Física (PHY)
//=======================================================================
void Phy_initialize() {
  Serial.begin(TAXA_SERIAL);
  while(!Serial); // Espera a porta serial conectar
  
  inicializa_lora(); // Agora esta função realmente configura o módulo
}

// Esta função agora configura o módulo para um estado ótimo e conhecido
void inicializa_lora() {
  e220ttl.begin();

  // Entra em modo de configuração
  ResponseStatus rs = e220ttl.setMode(MODE_3_CONFIGURATION);
  if (rs.code != 1) {
    Serial.println("FALHA CRÍTICA AO ENTRAR EM MODO DE CONFIGURACAO!");
    while (1);
  }

  // Cria a estrutura de configuração
  Configuration config;
  config.ADDL = MY_ID & 0xFF;
  config.ADDH = 0;
  config.CHAN = 23; // Canal de comunicação
  
  // Parâmetros otimizados
  config.SPED.airDataRate = AIR_DATA_RATE_2400_8N1;
  config.SPED.uartBaudRate = UART_BPS_9600; // SoftwareSerial é mais estável em 9600
  config.SPED.uartParity = MODE_00_8N1;
  config.OPTION.fec = FEC_1_ON;
  config.OPTION.fixedTransmission = FT_FIXED_TRANSMISSION;
  config.OPTION.transmissionPower = POWER_30; // Potência máxima do seu módulo
  config.OPTION.wirelessWakeupTime = WAKE_UP_250;

  // Grava a configuração no módulo
  e220ttl.setConfiguration(config);

  // Volta para o modo normal para operação
  e220ttl.setMode(MODE_0_NORMAL);
}

void Phy_serial_receive() {
  if (Serial.available() >= TAMANHO_PACOTE) {
    for (byte i = 0; i < TAMANHO_PACOTE; i++) {
      PacoteDL[i] = Serial.read();
    }
    Mac_serial_receive();
  }
}

void Phy_radio_receive() {
  // A função available() na biblioteca para ESP8266 retorna o tamanho do pacote
  if (e220ttl.available() > 0) {
    ResponseContainer rc = e220ttl.receiveMessage(TAMANHO_PACOTE);
    
    // Se a recepção foi bem-sucedida e o tamanho bate
    if (rc.code == 1 && rc.data.length() == TAMANHO_PACOTE) {
      // Copia os dados recebidos para o buffer PacoteUL
      memcpy(PacoteUL, rc.data.c_str(), TAMANHO_PACOTE);
      
      // Guarda o RSSI do último pacote
      RSSI_dBm_UL = rc.rssi;
      
      Mac_radio_receive();
    }
  }
}

// SAÍDA PARA O SCRIPT PYTHON - MANTIDA EXATAMENTE IGUAL
void Phy_serial_send() {
  Phy_dBm_to_Radiuino();
  
  PacoteUL[RSSI_UPLINK] = RSSI_UL;
  PacoteUL[LQI_UPLINK] = LQI_UL;
  
  // Transmissão do pacote pela serial, byte a byte, sem modificações.
  for (int i = 0; i < TAMANHO_PACOTE; i++) {
    Serial.write(PacoteUL[i]);
  }
}

void Phy_radio_send() {
  // Pega o ID do destinatário do pacote que veio da borda
  byte destinatarioID = PacoteDL[RECEIVER_ID];
  byte canal = 23; // Canal deve ser o mesmo
  
  e220ttl.sendFixedMessage(0, destinatarioID, canal, PacoteDL, TAMANHO_PACOTE);
}

// Função de conversão - MANTIDA EXATAMENTE IGUAL
void Phy_dBm_to_Radiuino() {
  if(RSSI_dBm_UL > -10.5) {
   RSSI_UL = 127;
   LQI_UL = 1;
  }
  if(RSSI_dBm_UL <= -10.5 && RSSI_dBm_UL >= -74) {
   RSSI_UL = ((RSSI_dBm_UL +74)*2);
   LQI_UL = 0;
  }
  if(RSSI_dBm_UL < -74) {
   RSSI_UL = (((RSSI_dBm_UL +74)*2)+256);
   LQI_UL = 0;
  }
}


//=======================================================================
//                Camadas MAC e NET (Mantidas Idênticas)
//=======================================================================
void Mac_initialize() {}

void Mac_serial_receive() {
  Net_serial_receive();
}

void Mac_radio_receive() {
  Net_radio_receive();
}

void Mac_serial_send() {
  Phy_serial_send();
}

void Mac_radio_send() {
  Phy_radio_send();
}

void Net_initialize() {}

void Net_serial_receive() {
  // Quando um comando vem da borda (PC), ele é enviado para o rádio
  Net_radio_send();
}

void Net_radio_receive() {
  // Quando um pacote vem do rádio e é para este dispositivo, ele é enviado para a borda (PC)
  if (PacoteUL[RECEIVER_ID] == MY_ID) {
    Net_serial_send();
  }
}

void Net_serial_send() {
  Mac_serial_send();
}

void Net_radio_send() {
  Mac_radio_send();
}