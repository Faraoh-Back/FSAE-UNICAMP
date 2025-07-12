void App_initialize() {

}

void App_radio_receive() { 
  App_radio_send(); 
}

void App_radio_send() {
  Serial.println("Pacote recebido, enviando resposta...");
  Transp_radio_send();
}