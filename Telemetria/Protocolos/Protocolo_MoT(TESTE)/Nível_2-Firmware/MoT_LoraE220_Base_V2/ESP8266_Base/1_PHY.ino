void Phy_initialize() {  // Funcao de inicializacao da camada Física
  Serial.begin(TAXA_SERIAL);
  Serial.println("\n\n>>> Placa ESP8266 iniciada com sucesso! <<<");

  // --- MUDANÇA: Inicializa a SoftwareSerial com a taxa de 9600 (padrão do E220) ---
  loraSerial.begin(9600); 

  inicializa_lora();

  configureLoraModule();
}

void Phy_serial_receive() {  // Funcao de recepcao de pacote da Camada Física
  //===================== RECEPCAO DO PACOTE DL
  if (Serial.available() >= TAMANHO_PACOTE) {  // Testa se tem 52 bytes na serial

    for (byte i = 0; i < TAMANHO_PACOTE; i++)  // PacoteUL[#] é preenchido com zero e PacoteDL[#] recebe os bytes do buffer
    {
      PacoteDL[i] = Serial.read();  // Zera o pacote de transmissão
      PacoteUL[i] = 1;              // Faz a leitura dos bytes do pacote que estão no buffer da serial
      delay(1);                     // Intervalo de 1 ms para cada ciclo do for para estabilidade
    }


    //===================== SUBIDA DO PACOTE PARA A CAMADA MAC
    Mac_serial_receive();  // chama a funcao de recepcao da camada de controle de acesso ao meio
  }
}

void Phy_radio_receive() {
  if (e220ttl.available()) {
    ResponseContainer rc = e220ttl.receiveMessageRSSI();
    String receivedMessage = rc.data;

    // Condição para processar apenas se o tamanho for o esperado
    if (receivedMessage.length() == TAMANHO_PACOTE) {
        Serial.println("\n--- PACOTE LORA RECEBIDO PELA BASE ---");

        // CORREÇÃO: Salve a mensagem recebida no PACOTE DE RECEBIMENTO (DL = Downlink)
        receivedMessage.getBytes(PacoteDL, TAMANHO_PACOTE + 1); // <--- CORREÇÃO AQUI

        int rssiValue = rc.rssi;
        RSSI_dBm_UL = -1* (256-rssiValue);
        Serial.print("RSSI da resposta: ");
        Serial.print(RSSI_dBm_UL);
        Serial.println(" dBm");

        // Agora, continue o processamento do pacote recebido
        Mac_radio_receive();
    }
  }
}

//===================== TRANSMISSAO DO PACOTE DE TRANSMISSAO
void Phy_serial_send()  // Funcao de envio de pacote da Camada Física
{
  Phy_dBm_to_Radiuino();
  
  // =================Informações de gerência do pacote
  PacoteUL[RSSI_UPLINK] = RSSI_UL;  // aloca RSSI_UL
  PacoteUL[LQI_UPLINK] = LQI_UL;  // aloca LQI_UL
  // PacoteUL[RSSI_DOWNLINK] = PacoteDL[RSSI_DOWNLINK];
  // PacoteUL[LQI_DOWNLINK] = PacoteDL[LQI_DOWNLINK];

                          // TRANSMISSaO DO PACOTE TX
  // PacoteUL[UL_COUNTER_MSB] = PacoteDL[UL_COUNTER_MSB];
  // PacoteUL[UL_COUNTER_LSB] = PacoteDL[UL_COUNTER_LSB];
  // PacoteUL[DL_COUNTER_MSB] = PacoteDL[DL_COUNTER_MSB];
  // PacoteUL[DL_COUNTER_LSB] = PacoteDL[DL_COUNTER_LSB];
  // Transmissão do pacote pela serial do Arduino
  for (int i = 0; i < 52; i++) {
    Serial.write(PacoteUL[i]);
  }
}

void Phy_radio_send() {
  // rf95.send(PacoteDL, sizeof(PacoteDL));
  // rf95.waitPacketSent();
  // // for (int i = 0; i < sjze; i++) {
  // //   Serial.println(data[i]);
  // //   rf95.send(data, sizeof(data));
  // //   rf95.waitPacketSent();
  // //   delay(20);
  // // }
  e220ttl.sendMessage(PacoteUL, TAMANHO_PACOTE);

}

void inicializa_lora() {
  // ShowSerial.begin(TAXA_SERIAL);
  // if (!rf95.init()) {
  //   ShowSerial.println("Inicialização Falhou");
  //   while (1)
  //     ;
  // }
  // rf95.setFrequency(FREQUENCY_IN_MHZ);
  // rf95.setTxPower(POWER_TX_DBM); 
  
  // Startup all pins and UART
  e220ttl.begin();
  //delay(2000);

}

void Phy_dBm_to_Radiuino() // Função que transforma RSSI em dBm da leitura do LoRa para RSSI utilizada no MoT (complemento de 2 com passo 1/2 e 74 de offset)
{
  /*tabela usada durante a criação da função
   *   dBm     RSSI  
   *  -10,5   127
   *  -74     0
   *  -138    128
   *  -74,5   255
   */
   
  if(RSSI_dBm_UL > -10.5)  // Caso a RSSI medida esteja acima do valor superior -10,5 dBm
  {
   RSSI_UL = 127; // equivalente a -10,5 dBm 
   LQI_UL = 1;    // alerta que alcançou saturação no byte de LQI
  }

  if(RSSI_dBm_UL <= -10.5 && RSSI_dBm_UL >= -74) // Caso a RSSI medida esteja no intervalo [-10,5 dBm e -74 dBm]
  {
   RSSI_UL = ((RSSI_dBm_UL +74)*2) ;
   LQI_UL = 0;
  }

  if(RSSI_dBm_UL < -74) // Caso a RSSI medida esteja no intervalo ]-74 dBm e -138 dBm]
  {
   RSSI_UL = (((RSSI_dBm_UL +74)*2)+256) ;
   LQI_UL = 0;
  }
}

// Adicione esta função completa no arquivo 1_PHY.ino

// Cole esta função completa no seu arquivo 1_PHY.ino
void configureLoraModule() {
  Serial.println("Iniciando configuracao do modulo LoRa...");

  // 1. Obter a configuração atual do módulo
  // A biblioteca retorna um container. É preciso extrair os dados de dentro dele.
  ResponseStructContainer c;
  c = e220ttl.getConfiguration();
  
  // Verifique se a leitura foi bem-sucedida antes de continuar
  if (c.status.code != E220_SUCCESS) {
    Serial.print("ERRO! Falha ao ler a configuracao do modulo: ");
    Serial.println(c.status.getResponseDescription());
    return; // Aborta a função se não conseguiu ler
  }

  // Copia os dados para uma struct local para podermos modificá-los
  Configuration configuration = *(Configuration*)c.data;
  Serial.println("Configuracao atual lida com sucesso.");

  // 2. Modificar os parâmetros para corresponder ao script Python
  Serial.println("Aplicando novas configuracoes para corresponder ao no sensor...");

  // --- Parâmetros de Velocidade (corresponde ao 0x62 do Python) ---
  configuration.SPED.uartBaudRate = UART_BPS_9600;      // UART 9600bps
  configuration.SPED.airDataRate = AIR_DATA_RATE_010_24; // Air Data Rate 2.4kbps
  configuration.SPED.uartParity = MODE_00_8N1;         // Paridade 8N1

  // --- Canal de Frequência (corresponde ao 0x41 do Python) ---
  // 0x41 em hexadecimal é 65 em decimal. Frequência = 850 + 65 = 915 MHz.
  configuration.CHAN = 0x41;

  // --- Opções de Transmissão (corresponde ao 0x44 do Python) ---
  // Ativa o envio do RSSI junto com o pacote
  configuration.TRANSMISSION_MODE.enableRSSI = RSSI_ENABLED;
  // Define a potência de transmissão
  configuration.OPTION.transmissionPower = POWER_22; // 22dBm (ajuste se necessário, mas deve ser igual nos dois lados)
  
  // 3. Salvar a nova configuração no módulo
  // O parâmetro WRITE_CFG_PWR_DWN_SAVE garante que a configuração persista após desligar.
  ResponseStatus rs = e220ttl.setConfiguration(configuration, WRITE_CFG_PWR_DWN_SAVE);

  // 4. Verificar o resultado
  if (rs.code == E220_SUCCESS) {
    Serial.println(">>> Configuracao do modulo LoRa aplicada e salva com SUCESSO! <<<");
  } else {
    Serial.print("ERRO! Falha ao salvar a nova configuracao: ");
    Serial.println(rs.getResponseDescription());
  }

  // Libera a memória alocada pelo container
  c.close();
}