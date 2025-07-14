/*
  MoT LoRa | WissTek IoT
  Desenvolvido por: Victor Gomes e Raphael Montali da Assumpção
*/

//=======================================================================
//                     1 - Bibliotecas
//=======================================================================
#include "Bibliotecas.h"  // Arquivo contendo declaração de bibliotecas e variáveis

//=======================================================================
//                     2 - Variáveis
//=======================================================================
// As variávies utlizadas estão no arquivo de bibliotecas

//=======================================================================
//                     3 - Setup de inicialização
//=======================================================================

void printParameters(struct Configuration configuration) {
  Serial.println("----------------------------------------");
  Serial.println("      PARAMETROS ATUAIS DO MODULO (BASE ESP8266)");
  Serial.println("----------------------------------------");

  Serial.print(F("Frequencia       : "));  Serial.print(configuration.getChannelDescription()); Serial.println();
  Serial.print(F("Endereco         : "));  Serial.print(configuration.ADDH, HEX); Serial.print(configuration.ADDL, HEX); Serial.println();
  Serial.print(F("Baud Rate UART   : "));  Serial.println(configuration.SPED.getUARTBaudRateDescription());
  Serial.print(F("Velocidade no Ar : "));  Serial.println(configuration.SPED.getAirDataRateDescription());
  Serial.print(F("Potencia         : "));  Serial.println(configuration.OPTION.getTransmissionPowerDescription());
  Serial.print(F("Modo de Envio    : "));  Serial.println(configuration.TRANSMISSION_MODE.getFixedTransmissionDescription());
  Serial.print(F("RSSI Ativado     : "));  Serial.println(configuration.TRANSMISSION_MODE.getRSSIEnableByteDescription());
  Serial.println("----------------------------------------");
}

// Inicializa as camadas
void setup() {
  Serial.begin(TAXA_SERIAL);
  delay(1000);
  Phy_initialize();     // Inicializa a camada Física
  Mac_initialize();     // Inicializa a camada de Controle de Acesso ao Meio
  Net_initialize();     // Inicializa a camada de Rede

  // --- ADICIONE ESTA CHAMADA ---
  Serial.println("\nLendo a configuracao final do modulo para verificacao...");
  ResponseStructContainer c = e220ttl.getConfiguration();
  if (c.status.code == E220_SUCCESS){
    printParameters(*(Configuration*)c.data);
  } else {
    Serial.println("Nao foi possivel ler a configuracao para imprimir!");
  }
  c.close();
}

//=======================================================================
//                     4 - Loop de repetição
//=======================================================================
// A função loop irá executar repetidamente
// Variável para controlar o tempo
unsigned long previousMillis = 0;
const long interval = 10000; // Intervalo de 10 segundos

void loop() {
  // ADICIONE ESTA LINHA para que o ESP sempre escute o rádio

  // A lógica de envio a cada 10 segundos continua a mesma
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    
    Serial.println("\nEnviando pacote de teste para o no sensor (ID 100)...");
    
    // Limpar pacote UL
    memset(PacoteUL, 0, TAMANHO_PACOTE);
    
    // Configurar cabeçalho do pacote
    PacoteUL[RECEIVER_ID] = SENSOR_ID;    // Para a Raspberry Pi
    PacoteUL[TRANSMITTER_ID] = MY_ID;     // Da Base (ESP8266)
    
    // Incrementar contador
    contadorUL++;
    PacoteUL[UL_COUNTER_MSB] = (contadorUL >> 8) & 0xFF;
    PacoteUL[UL_COUNTER_LSB] = contadorUL & 0xFF;

    // Adiciona dados de teste na camada de aplicação para visualização
    PacoteUL[APP1] = 0xAA;
    PacoteUL[APP2] = 0xBB;
    
    // Dados de teste na camada de aplicação
    PacoteUL[APP1] = 0xAA; // Byte de teste
    PacoteUL[APP2] = 0xBB; // Byte de teste
    
    Serial.print("Contador UL: ");
    Serial.println(contadorUL);

    // ===================================================================
    //          BLOCO DE DEBUG PARA VER O PACOTE DE ENVIO
    // ===================================================================
    Serial.println("--- [ESP8266] Conteudo do PacoteUL a ser enviado (HEX): ---");
    for (int i = 0; i < TAMANHO_PACOTE; i++) {
      if (PacoteUL[i] < 0x10) {
        Serial.print("0"); // Adiciona um zero à esquerda para formatação
      }
      Serial.print(PacoteUL[i], HEX);
      Serial.print(" ");
    }
    Serial.println("\n------------------------------------------------------------------");
    // ===================================================================
    
    // Enviar pacote
    Phy_radio_send();
  }

  Phy_radio_receive();
  delay(50);
}

void printParameters(struct Configuration configuration) {
  Serial.println("----------------------------------------");
  Serial.println("         PARAMETROS DO MODULO LORA (ESP8266)      ");
  Serial.println("----------------------------------------");

  Serial.print(F("Frequencia       : "));  Serial.print(configuration.getChannelDescription()); Serial.println();
  Serial.print(F("Endereco         : "));  Serial.print(configuration.ADDH, HEX); Serial.print(configuration.ADDL, HEX); Serial.println();
  Serial.print(F("Paridade UART    : "));  Serial.println(configuration.SPED.getUARTParityDescription());
  Serial.print(F("Baud Rate UART   : "));  Serial.println(configuration.SPED.getUARTBaudRateDescription());
  Serial.print(F("Velocidade no Ar : "));  Serial.println(configuration.SPED.getAirDataRateDescription());
  Serial.print(F("Potencia         : "));  Serial.println(configuration.OPTION.getTransmissionPowerDescription());
  Serial.print(F("RSSI Ativado     : "));  Serial.println(configuration.TRANSMISSION_MODE.getRSSIEnableByteDescription());

  Serial.println("----------------------------------------");
}