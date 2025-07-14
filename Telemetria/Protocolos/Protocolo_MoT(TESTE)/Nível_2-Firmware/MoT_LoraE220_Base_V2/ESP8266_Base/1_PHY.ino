//=======================================================================
// CAMADA FÍSICA (PHY)
//=======================================================================
void Phy_initialize() {
  loraSerial.begin(9600);
  
  // Inicializar módulo LoRa
  inicializa_lora();
  
}

void inicializa_lora() {  
  // Inicializar todos os pinos e UART
  e22ttl.begin();
  delay(2000); // Dar tempo para o módulo estabilizar
  
  // 1. Obtém a configuração atual do módulo
  ResponseStructContainer c;
  c = e22ttl.getConfiguration();
  Configuration configuration = *(Configuration*) c.data;
  Serial.println(c.status.getResponseDescription());
  
  if (c.status.code != E22_SUCCESS) {
      Serial.println("ERRO CRITICO AO LER CONFIGURACAO INICIAL!");
      while(1);
  }

  // 2. Modifica os parametros para a compatibilidade com o script da Pi
  configuration.ADDL = 0x01; // Endereço de hardware da Base = 1
  configuration.ADDH = 0x00;
  configuration.NETID = 0x00;

  configuration.CHAN = 65; // Canal para 915 MHz (850MHz + 65)

  configuration.SPED.uartBaudRate = UART_BPS_9600;
  configuration.SPED.airDataRate = AIR_DATA_RATE_010_24;
  configuration.SPED.uartParity = MODE_00_8N1;

  // Usa 22dBm para ser compatível com o byte 0xC4 do script Python
  configuration.OPTION.subPacketSetting = SPS_240_00;
  configuration.OPTION.RSSIAmbientNoise = RSSI_AMBIENT_NOISE_DISABLED;
  configuration.OPTION.transmissionPower = POWER_22;
  
  // Parâmetros de modo de transmissão
  configuration.TRANSMISSION_MODE.enableRSSI = RSSI_ENABLED;
  configuration.TRANSMISSION_MODE.fixedTransmission = FT_TRANSPARENT_TRANSMISSION;
  configuration.TRANSMISSION_MODE.enableRepeater = REPEATER_DISABLED;
  configuration.TRANSMISSION_MODE.enableLBT = LBT_DISABLED;
  configuration.TRANSMISSION_MODE.WORTransceiverControl = WOR_RECEIVER;
  configuration.TRANSMISSION_MODE.WORPeriod = WOR_2000_011;

  // 3. Salva a nova configuração no módulo
  ResponseStatus rs = e22ttl.setConfiguration(configuration, WRITE_CFG_PWR_DWN_SAVE);

  delay(20000);

  if (rs.code == E22_SUCCESS) {
    Serial.println("PHY: Configuração do módulo aplicada com SUCESSO!");
  } else {
    Serial.print("ERRO! Falha ao salvar configuração: ");
    while(1);
  }

  c.close(); // Liberar memória
}

void Phy_radio_receive() {
  if (e22ttl.available()) {
    // A função receiveMessage retorna um container com os dados
    ResponseContainer rc = e22ttl.receiveMessage();
    
    if (rc.status.code == E22_SUCCESS) {
      if (rc.data.length() >= TAMANHO_PACOTE) {
        Serial.println("\n--- PACOTE LORA RECEBIDO PELA BASE ---");
        
        // Copia os dados para o PacoteDL (Downlink da perspectiva da Base)
        memcpy(PacoteDL, rc.data.c_str(), TAMANHO_PACOTE);

        // A biblioteca LoRa_E22 não anexa o RSSI, ele precisa ser solicitado
        // Vamos simular ou pegar de uma futura mensagem de status
        RSSI_dBm_UL = -50; // Valor simulado
        
        Serial.print("Recebido do No Sensor (ID ");
        Serial.print(PacoteDL[TRANSMITTER_ID]);
        Serial.println(")");

        Mac_radio_receive();
      }
    }
  }
}

void Phy_radio_send() {
  Serial.println("Enviando chamado para o no sensor...");
  // Envia o PacoteUL para o endereço do Sensor (Pi) no canal configurado
  ResponseStatus rs = e22ttl.sendFixedMessage(0, SENSOR_ID, 65, PacoteUL, TAMANHO_PACOTE);
  if (rs.code != E22_SUCCESS) {
    Serial.println("Falha ao enviar pacote!");
  }
}

/*void Phy_dBm_to_Radiuino() {
  // Converter RSSI dBm para formato Radiuino
  if (RSSI_dBm_UL > -10.5) {
    RSSI_UL = 127;
    LQI_UL = 1;
  } else if (RSSI_dBm_UL <= -10.5 && RSSI_dBm_UL >= -74) {
    RSSI_UL = ((RSSI_dBm_UL + 74) * 2);
    LQI_UL = 0;
  } else if (RSSI_dBm_UL < -74) {
    RSSI_UL = (((RSSI_dBm_UL + 74) * 2) + 256);
    LQI_UL = 0;
  }
}*/