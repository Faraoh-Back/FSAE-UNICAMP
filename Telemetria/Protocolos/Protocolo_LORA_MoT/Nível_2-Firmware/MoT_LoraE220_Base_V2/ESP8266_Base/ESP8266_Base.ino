/*
  MoT LoRa | WissTek IoT
  Desenvolvido por: Victor Gomes e Raphael Montali da Assumpção
*/

//=======================================================================
//                     1 - Bibliotecas
//=======================================================================
#include "Bibliotecas.h"  // Arquivo contendo declaração de bibliotecas e variáveis


// funções
void printParameters(struct Configuration configuration); // Função de diagnóstico
//=======================================================================
//                     2 - Variáveis
//=======================================================================
// As variávies utlizadas estão no arquivo de bibliotecas

//=======================================================================
//                     3 - Setup de inicialização
//=======================================================================
// Inicializa as camadas
void setup() {
  Serial.begin(TAXA_SERIAL);
  while (!Serial); // Espera a porta serial conectar
  delay(1000);

  Phy_initialize();     // Inicializa a camada Física
  Mac_initialize();     // Inicializa a camada de Controle de Acesso ao Meio
  Net_initialize();     // Inicializa a camada de Rede

  // --- ADICIONE ESTA CHAMADA ---
  Serial.println("\nLendo a configuracao final do modulo para verificacao...");
  ResponseStructContainer c = e22ttl.getConfiguration();
  if (c.status.code == E22_SUCCESS){
    printParameters(*(Configuration*)c.data);
  } else {
    Serial.println("Nao foi possivel ler a configuracao para imprimir!");
  }
  c.close();
  
  Serial.println("\n--- Base LoRa (ESP8266) Pronta ---");
}

//=======================================================================
//                     3 - Loop de repetição
//=======================================================================
unsigned long previousMillis = 0;

void loop() {
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= INTERVALO_POLL) {
    previousMillis = currentMillis;
    
    // Limpa e prepara o pacote de chamada (Uplink da perspectiva da Base)
    memset(PacoteUL, 0, TAMANHO_PACOTE);
    PacoteUL[RECEIVER_ID] = SENSOR_ID; // Destinatário é o Pi (ID 100)
    PacoteUL[TRANSMITTER_ID] = MY_ID;   // Remetente sou eu (ID 1)
    
    // Adiciona dados de teste para o Pi visualizar
    PacoteUL[APP1] = 0xDE;
    PacoteUL[APP2] = 0xAD;

    // Envia o pacote de chamada
    Phy_radio_send();
  }
  // Ouve continuamente por respostas
  Phy_radio_receive();
}

// FUNÇÃO DE DIAGNÓSTICO - Exatamente como você pediu
void printParameters(struct Configuration configuration) {
  Serial.println("----------------------------------------");

  Serial.print(F("HEAD : "));  Serial.print(configuration.COMMAND, HEX);Serial.print(" ");Serial.print(configuration.STARTING_ADDRESS, HEX);Serial.print(" ");Serial.println(configuration.LENGHT, HEX);
  Serial.println(F(" "));
  Serial.print(F("AddH : "));  Serial.println(configuration.ADDH, HEX);
  Serial.print(F("AddL : "));  Serial.println(configuration.ADDL, HEX);
  Serial.println(F(" "));
  Serial.print(F("Chan : "));  Serial.print(configuration.CHAN, DEC); Serial.print(" -> "); Serial.println(configuration.getChannelDescription());
  Serial.println(F(" "));
  Serial.print(F("SpeedParityBit     : "));  Serial.print(configuration.SPED.uartParity, BIN);Serial.print(" -> "); Serial.println(configuration.SPED.getUARTParityDescription());
  Serial.print(F("SpeedUARTDatte     : "));  Serial.print(configuration.SPED.uartBaudRate, BIN);Serial.print(" -> "); Serial.println(configuration.SPED.getUARTBaudRateDescription());
  Serial.print(F("SpeedAirDataRate   : "));  Serial.print(configuration.SPED.airDataRate, BIN);Serial.print(" -> "); Serial.println(configuration.SPED.getAirDataRateDescription());
  Serial.println(F(" "));
  Serial.print(F("OptionTranPower    : "));  Serial.print(configuration.OPTION.transmissionPower, BIN);Serial.print(" -> "); Serial.println(configuration.OPTION.getTransmissionPowerDescription());
  Serial.println(F(" "));
  Serial.print(F("TransModeFixedTrans: "));  Serial.print(configuration.TRANSMISSION_MODE.fixedTransmission, BIN);Serial.print(" -> "); Serial.println(configuration.TRANSMISSION_MODE.getFixedTransmissionDescription());
  Serial.print(F("TransModeEnableRSSI: "));  Serial.print(configuration.TRANSMISSION_MODE.enableRSSI, BIN);Serial.print(" -> "); Serial.println(configuration.TRANSMISSION_MODE.getRSSIEnableByteDescription());

  Serial.println("----------------------------------------");
}