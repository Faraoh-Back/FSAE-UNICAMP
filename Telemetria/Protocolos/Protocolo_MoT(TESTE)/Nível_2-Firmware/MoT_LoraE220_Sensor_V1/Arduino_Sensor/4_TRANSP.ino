void Transp_initialize() {}
void Transp_radio_receive() { 
  App_radio_receive(); 
}

void Transp_radio_send() {
  contadorUL++;
  PacoteUL[UL_COUNTER_MSB] = (byte)(contadorUL >> 8);
  PacoteUL[UL_COUNTER_LSB] = (byte)(contadorUL & 0xFF);
  Net_radio_send();
}