/*
  MoT LoRa | WissTek IoT
  Desenvolvido por: Victor Gomes e Raphael Montali da Assumpção
*/

//=======================================================================
//                     1 - Bibliotecas
//=======================================================================
#include "Bibliotecas.h"  // Arquivo contendo declaração de bibliotecas e variáveis

//=======================================================================
//                     Protótipos das Funções
//=======================================================================
void Phy_initialize(); void inicializa_lora(); void Phy_radio_receive(); void Phy_radio_send(); void Phy_dBm_to_Radiuino();
void Mac_initialize(); void Mac_radio_receive(); void Mac_radio_send();
void Net_initialize(); void Net_radio_receive(); void Net_radio_send();
void Transp_initialize(); void Transp_radio_receive(); void Transp_radio_send();
void App_initialize(); void App_radio_receive(); void App_radio_send();

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
  Transp_initialize();
  App_initialize();
  Serial.println("--- No LoRa (Arduino + E22) Pronto ---");
}

//=======================================================================
//                     4 - Loop de repetição
//=======================================================================
// A função loop irá executar repetidamente
void loop() {
  Phy_radio_receive();
}
