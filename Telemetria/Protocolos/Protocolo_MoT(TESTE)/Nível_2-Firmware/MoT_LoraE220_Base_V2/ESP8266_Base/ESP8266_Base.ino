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
// Inicializa as camadas
void setup() {
  Serial.begin(TAXA_SERIAL);

  Phy_initialize();     // Inicializa a camada Física
  Mac_initialize();     // Inicializa a camada de Controle de Acesso ao Meio
  Net_initialize();     // Inicializa a camada de Rede
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
  Phy_radio_receive();

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
    
    // Dados de teste na camada de aplicação
    PacoteUL[APP1] = 0xAA; // Byte de teste
    PacoteUL[APP2] = 0xBB; // Byte de teste
    
    Serial.print("Contador UL: ");
    Serial.println(contadorUL);
    
    // Enviar pacote
  }

  delay(50);
}