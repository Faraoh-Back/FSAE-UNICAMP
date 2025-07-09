void Transp_initialize() {

}

void Transp_radio_receive() {
  App_radio_receive();
}

void Transp_radio_send() {
  contadorUL = contadorUL + 1;
  // PacoteUL[UL_COUNTER_MSB] =(byte)contadorUL/256;
  // PacoteUL[UL_COUNTER_LSB] = (byte)contadorUL%256;
  Net_radio_send();
}
