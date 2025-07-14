void Mac_initialize() {
  Serial.println("MAC: Camada MAC inicializada.");
}

void Mac_radio_receive() {
  Serial.println("MAC: Processando pacote recebido...");
  Net_radio_receive();
}

void Mac_radio_send() {
  Serial.println("MAC: Enviando pacote para camada física...");
  Phy_radio_send();
}