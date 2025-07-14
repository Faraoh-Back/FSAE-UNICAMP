void Net_initialize()  // Função de inicialização da camada de Rede
{
}

void Net_serial_receive()  // Função de recepção de pacote da Camada de Rede
{
  Net_radio_send();  // Demais camadas são tratadas no Python da Borda
}
// ====== FUNÇÃO RECEBE PAOCTE DA CAMDA DE REDE
// No ESP8266
void Net_radio_receive() {
  // A resposta do Pi foi salva em PacoteDL.
  // O código original verificava PacoteUL por engano.
  Serial.print("Rede: Resposta recebida. Verificando ID... (Esperado: ");
  Serial.print(MY_ID);
  Serial.print(", Recebido: ");
  Serial.print(PacoteDL[RECEIVER_ID]);
  Serial.println(")");
  
  if (PacoteDL[RECEIVER_ID] == MY_ID) { // <-- CORRIGIDO para usar PacoteDL
    Serial.println("Rede: ID Correto! Processando resposta.");
    Net_serial_send();
  } else {
    Serial.println("Rede: Resposta descartada, ID incorreto.");
  }
}

// ====== ENVIA PACOTE CAMADA REDE
void Net_serial_send()  // Função de envio de pacote da Camada de Rede
{
  Mac_serial_send();  //Chama a função de envio da Camada de Acesso ao Meio
}

void Net_radio_send() {
  Mac_radio_send();
}