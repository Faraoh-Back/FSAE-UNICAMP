//=======================================================================
// CAMADA FÍSICA (PHY)
//=======================================================================
void Phy_initialize() {
  Serial.println("PHY: Inicializando camada física...");
  
  // Inicializar SoftwareSerial com taxa de 9600 (padrão do E220)
  loraSerial.begin(9600);
  
  // Inicializar módulo LoRa
  inicializa_lora();
  
  // Configurar módulo para 915 MHz
  // configureLoraModule();
  
  Serial.println("PHY: Camada física inicializada com sucesso!");
}

void Phy_radio_receive() {
  if (e220ttl.available() > 0) {
    ResponseContainer rc = e220ttl.receiveMessageRSSI();
    
    if (rc.status.code == E220_SUCCESS) {
      String receivedMessage = rc.data;
      
      // Verificar se o tamanho está correto
      if (receivedMessage.length() == TAMANHO_PACOTE) {
        Serial.println("\n=== PACOTE LORA RECEBIDO ===");
        
        // Copiar dados recebidos para PacoteDL
        for (int i = 0; i < TAMANHO_PACOTE; i++) {
          PacoteDL[i] = receivedMessage[i];
        }
        
        // Processar RSSI
        int rssiValue = rc.rssi;
        RSSI_dBm_UL = -1 * (256 - rssiValue);
        
        Serial.print("RSSI: ");
        Serial.print(RSSI_dBm_UL);
        Serial.println(" dBm");
        
        Serial.print("Tamanho: ");
        Serial.print(receivedMessage.length());
        Serial.println(" bytes");
        
        // Mostrar IDs do pacote
        Serial.print("De ID: ");
        Serial.print(PacoteDL[TRANSMITTER_ID]);
        Serial.print(" Para ID: ");
        Serial.println(PacoteDL[RECEIVER_ID]);
        
        // Processar na camada MAC
        Mac_radio_receive();
      } else {
        Serial.print("PHY: Pacote com tamanho incorreto: ");
        Serial.println(receivedMessage.length());
      }
    }
  }
}

void Phy_radio_send() {
  // Converter RSSI para formato Radiuino
  Phy_dBm_to_Radiuino();
  
  // Adicionar informações de RSSI no pacote
  PacoteUL[RSSI_UPLINK] = RSSI_UL;
  PacoteUL[LQI_UPLINK] = LQI_UL;
  
  // Enviar mensagem
  ResponseStatus rs = e220ttl.sendMessage(PacoteUL, TAMANHO_PACOTE);
  
  if (rs.code == E220_SUCCESS) {
    Serial.println("PHY: Mensagem enviada com sucesso!");
  } else {
    Serial.print("PHY: Erro ao enviar mensagem: ");
    Serial.println(rs.getResponseDescription());
  }
}

void inicializa_lora() {
  Serial.println("PHY: Inicializando módulo E220...");
  
  // Inicializar todos os pinos e UART
  e220ttl.begin();
  
  delay(2000); // Dar tempo para o módulo estabilizar
  
  Serial.println("PHY: Módulo E220 inicializado.");
}

void configureLoraModule() {
  Serial.println("PHY: Configurando módulo LoRa para 915 MHz...");
  
  // Obter configuração atual
  ResponseStructContainer c = e220ttl.getConfiguration();
  
  if (c.status.code != E220_SUCCESS) {
    Serial.print("ERRO! Falha ao ler configuração: ");
    Serial.println(c.status.getResponseDescription());
    return;
  }
  
  // Copiar configuração para modificação
  Configuration configuration = *(Configuration*)c.data;
  
  // Configurar parâmetros (igual ao Python)
  configuration.SPED.uartBaudRate = UART_BPS_9600;        // 9600 bps
  configuration.SPED.airDataRate = AIR_DATA_RATE_010_24;  // 2.4 kbps
  configuration.SPED.uartParity = MODE_00_8N1;            // 8N1
  
  // Canal para 915 MHz (0x41 = 65 decimal, 850 + 65 = 915 MHz)
  configuration.CHAN = 0x41;
  
  // Opções de transmissão
  configuration.TRANSMISSION_MODE.enableRSSI = RSSI_ENABLED;
  configuration.OPTION.transmissionPower = POWER_22;      // 22dBm
  
  // Salvar configuração
  ResponseStatus rs = e220ttl.setConfiguration(configuration, WRITE_CFG_PWR_DWN_SAVE);
  
  if (rs.code == E220_SUCCESS) {
    Serial.println("PHY: Configuração do módulo aplicada com SUCESSO!");
  } else {
    Serial.print("ERRO! Falha ao salvar configuração: ");
    Serial.println(rs.getResponseDescription());
  }
  
  // Liberar memória
  c.close();
  
  Serial.println("PHY: Módulo configurado para 915 MHz com Air Data Rate 2.4 kbps");
}

void Phy_dBm_to_Radiuino() {
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
}