void Phy_initialize() {  // Funcao de inicializacao da camada Física
  Serial.begin(TAXA_SERIAL);
  inicializa_lora();
}

void inicializa_lora() {
  e22ttl.begin();

  // Esta biblioteca requer que você primeiro LEIA a configuração atual
  ResponseStructContainer c;
  c = e22ttl.getConfiguration();
  Configuration configuration = *(Configuration*) c.data;

  // Agora, modificamos os parâmetros que queremos alterar
  configuration.ADDL = MY_ID;
  configuration.CHAN = 65; // 65 para 915 MHz

  // A estrutura de configuração é diferente nesta biblioteca
  configuration.SPED.uartBaudRate = UART_BPS_9600;
  configuration.SPED.airDataRate = AIR_DATA_RATE_010_24; // 2.4kbps
  configuration.SPED.uartParity = MODE_00_8N1;
  
  configuration.OPTION.transmissionPower = POWER_22;
  
  // Modo de transmissão fixa é essencial para a lógica de endereçamento
  configuration.TRANSMISSION_MODE.fixedTransmission = FT_FIXED_TRANSMISSION;
  // Habilitar o envio de RSSI junto com o pacote
  configuration.TRANSMISSION_MODE.enableRSSI = RSSI_ENABLED;

  // Finalmente, gravamos a nova configuração no módulo
  ResponseStatus rs = e22ttl.setConfiguration(configuration, WRITE_CFG_PWR_DWN_SAVE);
  
  if (rs.code == E22_SUCCESS) {
    Serial.println("Configuracao do modulo LoRa salva com sucesso!");
  } else {
    Serial.println("Erro ao salvar configuracao!");
    while(1);
  }
  
  delete (Configuration*)c.data;
}

void Phy_radio_receive() {
  // Nesta biblioteca, o 'available' pode retornar o tamanho do pacote + 1 byte de RSSI
  if (e22ttl.available() > 1) { 
    ResponseContainer rc = e22ttl.receiveMessageRSSI();

    if (rc.status.code == E22_SUCCESS) {
        if(rc.data.length() >= TAMANHO_PACOTE){
            // Copia os dados da String para o array de bytes
            memcpy(PacoteDL, rc.data.c_str(), TAMANHO_PACOTE);
            RSSI_dBm_DL = rc.rssi;
            Mac_radio_receive();
        }
    }
  }
}

void Phy_radio_send() {
  Phy_dBm_to_Radiuino();
  PacoteUL[RSSI_DOWNLINK] = RSSI_DL;
  PacoteUL[LQI_DOWNLINK] = LQI_DL;

  // Envia o pacote de resposta para a base
  e22ttl.sendFixedMessage(0, ID_DA_BASE, 65, PacoteUL, TAMANHO_PACOTE);
}

void Phy_dBm_to_Radiuino() {
  if(RSSI_dBm_DL > -10.5) {
   RSSI_DL = 127; LQI_DL = 1;
  } else if(RSSI_dBm_DL <= -10.5 && RSSI_dBm_DL >= -74) {
   RSSI_DL = ((RSSI_dBm_DL + 74)*2); LQI_DL = 0;
  } else {
   RSSI_DL = (((RSSI_dBm_DL + 74)*2)+256); LQI_DL = 0;
  }
}
