void Net_initialize()  // Função de inicialização da camada de Rede
{
}

// ====== FUNÇÃO RECEBE PAOCTE DA CAMDA DE REDE
void Net_radio_receive() {
  if(PacoteDL[RECEIVER_ID] == MY_ID) {
    Transp_radio_receive();
  }
}
// ====== ENVIA PACOTE CAMADA REDE
void Net_radio_send() {
  PacoteUL[RECEIVER_ID] = PacoteDL[TRANSMITTER_ID];
  PacoteUL[TRANSMITTER_ID] = MY_ID;
  Mac_radio_send();
}
