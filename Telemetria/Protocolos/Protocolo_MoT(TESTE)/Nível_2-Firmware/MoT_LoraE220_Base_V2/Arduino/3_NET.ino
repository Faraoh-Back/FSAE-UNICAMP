void Net_initialize()  // Função de inicialização da camada de Rede
{
}

// ====== FUNÇÃO RECEBE PAOCTE DA CAMDA DE REDE
void Net_serial_receive()  // Função de recepção de pacote da Camada de Rede
{
  Net_radio_send();  // Demais camadas são tratadas no Python da Borda
}

void Net_radio_receive() {
  if (PacoteUL[RECEIVER_ID] == MY_ID) {
    Net_serial_send();  // Demais camadas são tratadas no Python da Borda
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
