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
    
    // Monta o pacote de uplink (UL)
    PacoteUL[RECEIVER_ID] = 100;      // Endereça para a Raspberry Pi
    PacoteUL[TRANSMITTER_ID] = MY_ID; // Diz que foi a Base (ID 1) que enviou
    
    // Envia o pacote
    Phy_radio_send();
  }
}
