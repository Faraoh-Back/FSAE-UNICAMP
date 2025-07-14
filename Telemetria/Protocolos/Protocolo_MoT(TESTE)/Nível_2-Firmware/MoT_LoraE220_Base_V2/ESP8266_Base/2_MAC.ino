void Mac_initialize() {  // Função de inicialização da camada de Acesso ao Meio
  // Nada aqui por enquanto
}

//================ RECEBE O PACOTE DA CAMADA FÍSICA
void Mac_serial_receive() {  // Função de recepção de pacote da Camada MAC
  Net_serial_receive();      // chama a função de recepção da camada de Rede
}

void Mac_radio_receive() {
  Net_radio_receive();
}
//================
void Mac_serial_send()  // Função de envio de pacote da Camada MAC
{
  Phy_serial_send();  //Chama a função de envio da Camada Física
}
void Mac_radio_send() {
  Phy_radio_send();
}