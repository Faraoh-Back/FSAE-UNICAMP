void Net_initialize() {
  Serial.println("NET: Camada de rede inicializada.");
}

void Net_radio_receive() {
  Serial.print("NET: Verificando destinatário... (Esperado: ");
  Serial.print(MY_ID);
  Serial.print(", Recebido: ");
  Serial.print(PacoteDL[RECEIVER_ID]);
  Serial.println(")");
  
  if (PacoteDL[RECEIVER_ID] == MY_ID) {
    Serial.println("NET: Pacote é para mim! Processando...");
    
    // Incrementar contador de downlink
    contadorDL++;
    
    // Mostrar informações do pacote
    Serial.print("NET: Pacote do transmissor ID: ");
    Serial.println(PacoteDL[TRANSMITTER_ID]);
    
  } else {
    Serial.println("NET: Pacote descartado - não é para mim.");
  }
}

void Net_radio_send() {
  Serial.println("NET: Preparando pacote para envio...");
  
  // Configurar roteamento (resposta)
  PacoteUL[RECEIVER_ID] = PacoteDL[TRANSMITTER_ID];  // Responder para quem enviou
  PacoteUL[TRANSMITTER_ID] = MY_ID;                  // Eu sou o transmissor
  
  Mac_radio_send();
}