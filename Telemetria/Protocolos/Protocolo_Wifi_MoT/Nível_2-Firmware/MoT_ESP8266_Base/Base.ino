// =======================================================================
//        FIRMWARE DE TESTE ESP8266 PARA O COLETOR PYTHON
// =======================================================================

// --- Configurações ---
#define TAMANHO_PACOTE 52
#define BAUDRATE 115200 // Deve ser o mesmo configurado no seu JSON

// --- Mapeamento do Pacote (Idêntico ao Python) ---
enum BytesDoPacote {
    RSSI_UPLINK = 0,
    RSSI_DOWNLINK = 2,
    DL_COUNTER_LSB = 13
};

// --- Buffers para os pacotes ---
byte pacote_recebido[TAMANHO_PACOTE];
byte pacote_envio[TAMANHO_PACOTE];

// =======================================================================
//                FUNÇÃO DE CODIFICAÇÃO DO RSSI
// =======================================================================
// Esta função faz o inverso da sua função "decodificar_rssi" em Python.
// Ela converte um valor de dBm para o formato de 1 byte que o script espera.
// Fórmula: byte = (dBm + 74) * 2
// =======================================================================
byte codificar_rssi_dbm(float dbm) {
  // Limita o valor de dBm para evitar overflow no byte
  if (dbm > -10.5) dbm = -10.5;
  if (dbm < -138) dbm = -138;

  int valor = (int)round((dbm + 74.0) * 2.0);

  // Garante que o valor está dentro do intervalo de um byte (0-255)
  if (valor < 0) valor = valor + 256;
  if (valor > 255) valor = 255;
  
  return (byte)valor;
}

// =======================================================================
//                          SETUP
// =======================================================================
void setup() {
  Serial.begin(BAUDRATE);
  while (!Serial); // Espera a porta serial conectar
  
  Serial.println("\n\nESP8266 pronto. Aguardando pacotes do script Python...");
}

// =======================================================================
//                          LOOP PRINCIPAL
// =======================================================================
void loop() {
  // 1. Verifica se um pacote completo de 52 bytes chegou do Python
  if (Serial.available() >= TAMANHO_PACOTE) {
    
    // 2. Lê o pacote de comando recebido
    Serial.readBytes(pacote_recebido, TAMANHO_PACOTE);
    
    // (Opcional) Imprime uma mensagem de debug para sabermos que o pacote chegou
    byte contador_dl = pacote_recebido[DL_COUNTER_LSB];
    Serial.print("Pacote de comando recebido (Contador DL: ");
    Serial.print(contador_dl);
    Serial.println("). Preparando resposta...");

    // 3. Simula os valores de RSSI que queremos enviar de volta
    float rssi_uplink_simulado = -45.5;
    float rssi_downlink_simulado = -62.0;

    // 4. Codifica os valores de RSSI para o formato de 1 byte
    byte rssi_ul_byte = codificar_rssi_dbm(rssi_uplink_simulado);
    byte rssi_dl_byte = codificar_rssi_dbm(rssi_downlink_simulado);

    // 5. Constrói o pacote de resposta
    memset(pacote_envio, 0, TAMANHO_PACOTE); // Limpa o buffer de envio
    pacote_envio[RSSI_UPLINK] = rssi_ul_byte;
    pacote_envio[RSSI_DOWNLINK] = rssi_dl_byte;
    // (Você pode preencher outros campos aqui se precisar no futuro)

    // 6. Envia ("printa") o pacote de resposta de 52 bytes de volta para o Python
    Serial.write(pacote_envio, TAMANHO_PACOTE);
  }
}