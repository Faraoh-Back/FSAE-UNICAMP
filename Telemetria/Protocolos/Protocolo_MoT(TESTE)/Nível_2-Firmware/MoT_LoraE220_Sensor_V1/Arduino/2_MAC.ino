void Mac_initialize() {  // Função de inicialização da camada de Acesso ao Meio
  // Nada aqui por enquanto
}

//================ RECEBE O PACOTE DA CAMADA FÍSICA
void Mac_radio_receive() {
  Net_radio_receive();
}

//================
void Mac_radio_send() {
  Phy_radio_send();
}
