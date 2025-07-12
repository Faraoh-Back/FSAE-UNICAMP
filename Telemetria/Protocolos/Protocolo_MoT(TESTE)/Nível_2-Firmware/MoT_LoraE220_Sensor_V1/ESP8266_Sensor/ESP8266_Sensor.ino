/*
  MoT LoRa | WissTek IoT - Nó Sensor para ESP8266
  Este firmware substitui o nó sensor Arduino. Ele é reativo:
  ouve por um chamado da base e envia uma resposta imediata.
*/

// =======================================================================
//                     1 - Bibliotecas
// =======================================================================
#include "Bibliotecas.h"  // Inclui nosso novo arquivo de cabeçalho

// =======================================================================
//                     Protótipos das Funções
// =======================================================================
void Phy_initialize(); void inicializa_lora(); void Phy_radio_receive(); void Phy_radio_send(); void Phy_dBm_to_Radiuino();
void Mac_initialize(); void Mac_radio_receive(); void Mac_radio_send();
void Net_initialize(); void Net_radio_receive(); void Net_radio_send();
void Transp_initialize(); void Transp_radio_receive(); void Transp_radio_send();
void App_initialize(); void App_radio_receive(); void App_radio_send();

// =======================================================================
//                     2 - Setup de inicialização
// =======================================================================
void setup() {
  Serial.begin(TAXA_SERIAL);
  while (!Serial);

  Phy_initialize();
  Mac_initialize();
  Net_initialize();
  Transp_initialize();
  App_initialize();
  Serial.println("\n--- No Sensor LoRa (ESP8266) Pronto ---");
  Serial.print("Meu ID: "); Serial.println(MY_ID);
  Serial.print("Aguardando chamado da Base ID: "); Serial.println(ID_DA_BASE);
  Serial.println("---------------------------------------");
}

// =======================================================================
//                     3 - Loop de repetição
// =======================================================================
void loop() {
  // A única tarefa do loop é ficar ouvindo o rádio por um chamado da base.
  Phy_radio_receive();
}

// =======================================================================
//                       CAMADA FÍSICA (PHY)
// =======================================================================
void Phy_initialize() {
  inicializa_lora();
}

void inicializa_lora() {
  loraSerial.begin(9600);
  e22ttl.begin();

  // Lê a configuração atual para poder modificá-la
  ResponseStructContainer c = e22ttl.getConfiguration();
  Configuration configuration = *(Configuration*) c.data;
  
  // Define os parâmetros para este nó sensor
  configuration.ADDL = MY_ID; // Define o endereço deste módulo
  configuration.CHAN = CANAL_LORA;
  
  configuration.SPED.uartBaudRate = UART_BPS_9600;
  configuration.SPED.airDataRate = AIR_DATA_RATE;
  configuration.SPED.uartParity = MODE_00_8N1;
  
  configuration.OPTION.transmissionPower = POTENCIA_TX;
  configuration.TRANSMISSION_MODE.fixedTransmission = FT_FIXED_TRANSMISSION;
  configuration.TRANSMISSION_MODE.enableRSSI = RSSI_ENABLED;

  // Grava a configuração na memória do módulo
  ResponseStatus rs = e22ttl.setConfiguration(configuration, WRITE_CFG_PWR_DWN_SAVE);
  if (rs.code == E22_SUCCESS) {
    Serial.println("Configuracao do modulo LoRa do Sensor salva com sucesso!");
  } else {
    Serial.println("ERRO CRITICO: Falha ao salvar configuracao do LoRa! Verifique a fiacao.");
    while(1); // Trava a execução em caso de erro
  }
  
  delete (Configuration*)c.data;
}

void Phy_radio_receive() {
  // Verifica se há pelo menos 2 bytes (1 de dado + 1 de RSSI)
  if (e22ttl.available() > 1) { 
    ResponseContainer rc = e22ttl.receiveMessageRSSI();

    if (rc.status.code == E22_SUCCESS) {
        if(rc.data.length() >= TAMANHO_PACOTE){
            // Copia os dados da String recebida para o nosso buffer de bytes
            memcpy(PacoteDL, rc.data.c_str(), TAMANHO_PACOTE);
            // Salva o RSSI do pacote que acabamos de receber da base
            RSSI_dBm_DL = rc.rssi;
            
            // Passa o pacote para a próxima camada
            Mac_radio_receive();
        }
    }
  }
}

void Phy_radio_send() {
  // Converte o RSSI medido para o formato do seu protocolo
  Phy_dBm_to_Radiuino();
  
  // Preenche os campos de status no pacote de resposta
  PacoteUL[RSSI_DOWNLINK] = RSSI_DL;
  PacoteUL[LQI_DOWNLINK] = LQI_DL;

  // Envia a resposta de volta para o endereço da base
  e22ttl.sendFixedMessage(0, ID_DA_BASE, CANAL_LORA, PacoteUL, TAMANHO_PACOTE);
}

void Phy_dBm_to_Radiuino() {
  // Função mantida idêntica ao seu código original
  if(RSSI_dBm_DL > -10.5) {
   RSSI_DL = 127; LQI_DL = 1;
  } else if(RSSI_dBm_DL <= -10.5 && RSSI_dBm_DL >= -74) {
   RSSI_DL = ((RSSI_dBm_DL + 74)*2); LQI_DL = 0;
  } else {
   RSSI_DL = (((RSSI_dBm_DL + 74)*2)+256); LQI_DL = 0;
  }
}


// =======================================================================
//         CAMADAS MAC, NET, TRANSPORTE E APP (Lógica Original)
// =======================================================================
// As funções abaixo foram mantidas idênticas ao seu código Arduino,
// pois a lógica de manipulação dos pacotes para montar a resposta
// é a mesma.

void Mac_initialize() {}
void Mac_radio_receive() {
  Net_radio_receive();
}
void Mac_radio_send() {
  Phy_radio_send();
}

void Net_initialize() {}
void Net_radio_receive() {
  // Se o pacote recebido da Base é para mim...
  if (PacoteDL[RECEIVER_ID] == MY_ID) {
    Transp_radio_receive();
  }
}
void Net_radio_send() {
  // Prepara o pacote de resposta com os IDs corretos
  PacoteUL[RECEIVER_ID] = PacoteDL[TRANSMITTER_ID]; // O novo destinatário é quem enviou
  PacoteUL[TRANSMITTER_ID] = MY_ID;                 // O remetente sou eu
  Mac_radio_send();
}

void Transp_initialize() {}
void Transp_radio_receive() { 
  App_radio_receive(); 
}
void Transp_radio_send() {
  // Incrementa o contador de pacotes enviados
  contadorUL++;
  PacoteUL[UL_COUNTER_MSB] = (byte)(contadorUL >> 8);
  PacoteUL[UL_COUNTER_LSB] = (byte)(contadorUL & 0xFF);
  Net_radio_send();
}

void App_initialize() {}
void App_radio_receive() { 
  // Neste momento, eu poderia ler sensores e preencher o PacoteUL com dados.
  // Como é um teste, apenas chamo a função para enviar a resposta.
  App_radio_send(); 
}
void App_radio_send() {
  Serial.print("Chamado da Base recebido! RSSI: ");
  Serial.print(RSSI_dBm_DL);
  Serial.println(" dBm. Enviando resposta...");
  
  // Aqui você preencheria o PacoteUL com dados reais de sensores, se tivesse.
  // Ex: PacoteUL[Data1] = (byte)leitura_do_sensor;
  
  Transp_radio_send();
}