void Phy_initialize() {  // Funcao de inicializacao da camada Física
  Serial.begin(TAXA_SERIAL);
  inicializa_lora();
}

void Phy_radio_receive() {
  // if (rf95.available()) {
  //   uint8_t len_pacote = TAMANHO_PACOTE;
  //   if (rf95.recv(PacoteDL, &len_pacote)) {
  //     if (len_pacote >= TAMANHO_PACOTE) {
  //       RSSI_dBm_DL = rf95.lastRssi();
  //       Mac_radio_receive();
  //     }
  //   }
  // }
  if (e220ttl.available()) {
    ResponseContainer rc = e220ttl.receiveMessageRSSI();  // Receive the message and RSSI value
    int rssiValue = rc.rssi;  // Get the RSSI value
    
    // Extract message and RSSI value
    String receivedMessage = rc.data;
    receivedMessage.getBytes(PacoteDL,receivedMessage.length());
    if (receivedMessage.length() == TAMANHO_PACOTE) {
        RSSI_dBm_DL = -1* (256-rssiValue);

        // //Debug
        
        // for(int i=0;i<52;i++){
        //   PacoteUL[i] = 1;
        //   Serial.print(PacoteDL[i]);
        //   Serial.print("-");
        // }
        // Serial.println();
        // Serial.println(receivedMessage.length());

      for(int i=0;i<52;i++){
          PacoteUL[i] = 1;
      }
        Mac_radio_receive();
    }
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

  Phy_dBm_to_Radiuino();
  PacoteUL[RSSI_DOWNLINK] = RSSI_DL;


  // //Debug
  // for(int i=0;i<52;i++){
  //   Serial.print(PacoteDL[i]);
  //   Serial.print("-");
  // }
  // Serial.println();
  // for(int i=0;i<52;i++){
  //   Serial.print(PacoteUL[i]);
  //   Serial.print("-");
  // }
  // Serial.println();
  // Serial.println(receivedMessage.length());


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

void Phy_dBm_to_Radiuino() // Função que transforma RSSI em dBm da leitura do WiFi para RSSI utilizada no radiuino (complemento de 2 com passo 1/2 e 74 de offset)
{
  /*tabela usada durante a criação da função
   *   dBm     RSSI  
   *  -10,5   127
   *  -74     0
   *  -138    128
   *  -74,5   255
   */
   
  if(RSSI_dBm_DL > -10.5)  // Caso a RSSI medida esteja acima do valor superior -10,5 dBm
  {
   RSSI_DL = 127; // equivalente a -10,5 dBm 
   LQI_DL = 1;    // alerta que alcançou saturação no byte de LQI
  }

  if(RSSI_dBm_DL <= -10.5 && RSSI_dBm_DL >= -74) // Caso a RSSI medida esteja no intervalo [-10,5 dBm e -74 dBm]
  {
   RSSI_DL = ((RSSI_dBm_DL +74)*2) ;
   LQI_DL = 0;
  }

  if(RSSI_dBm_DL < -74) // Caso a RSSI medida esteja no intervalo ]-74 dBm e -138 dBm]
  {
   RSSI_DL = (((RSSI_dBm_DL +74)*2)+256) ;
   LQI_DL = 0;
  }
  
  
}
