void Phy_initialize() {  // Funcao de inicializacao da camada Física
  Serial.begin(TAXA_SERIAL);
  inicializa_lora();
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
  // if (rf95.available()) {
  //   uint8_t len_pacote = TAMANHO_PACOTE;
  //   if (rf95.recv(PacoteDL, &len_pacote)) {
  //     if (len_pacote >= TAMANHO_PACOTE) {
  //       RSSI_dBm_UL = rf95.lastRssi();
  //       Mac_radio_receive();
  //     }
  //   }
  // }
  if (e220ttl.available()) {
    ResponseContainer rc = e220ttl.receiveMessageRSSI();  // Receive the message and RSSI value
    int rssiValue = rc.rssi;  // Get the RSSI value
    
    // Extract message and RSSI value
    String receivedMessage = rc.data;
    receivedMessage.getBytes(PacoteUL,receivedMessage.length());
    if (receivedMessage.length() == TAMANHO_PACOTE) {
        RSSI_dBm_UL = -1* (256-rssiValue);

        // //Debug
        // Serial.write(receivedMessage.length());
        // for(int i=0;i<52;i++){
        //   Serial.write(PacoteDL[i]);
        // }
        // Serial.println();
        // for(int i=0;i<52;i++){
        //   Serial.print(PacoteUL[i]);
        //   Serial.print("-");
        // }
        // Serial.println();





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
  e220ttl.sendMessage(PacoteDL, TAMANHO_PACOTE);

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
