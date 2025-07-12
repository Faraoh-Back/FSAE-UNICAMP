/*
========================================================================
        FIRMWARE DA BASE MESTRE PARA ESP8266
========================================================================

Função: Atuar como a "Base" ou "Professor" que inicia a comunicação.
Responsabilidades:
1.  Configurar o módulo LoRa para operar em 915 MHz.
2.  Periodicamente, enviar um "pacote de chamada" para a Raspberry Pi.
3.  Ouvir continuamente por uma resposta da Pi.
4.  Ao receber a resposta, imprimir os dados recebidos no Monitor Serial
    para visualização e debug.
*/

// =======================================================================
//                     1 - Bibliotecas e Protótipos
// =======================================================================
#include "Bibliotecas.h"

void inicializa_lora();
void enviarComandoParaSensor();
void receberRespostaDoSensor();
void imprimirRespostaDoSensor(int rssi);

// =======================================================================
//                     2 - Setup de inicialização
// =======================================================================
void setup() {
  Serial.begin(TAXA_SERIAL);
  while (!Serial);
  
  inicializa_lora();
  Serial.println("\n--- Base LoRa (ESP8266) Pronta ---");
  Serial.println("Modo: Mestre (Iniciando comunicação)");
}

// =======================================================================
//                     3 - Loop de Repetição
// =======================================================================
void loop() {
  // A cada X segundos, envia um comando de chamada para o sensor
  if (millis() - ultimoPoll >= INTERVALO_POLL) {
    ultimoPoll = millis(); // Reseta o timer
    enviarComandoParaSensor();
  }
  
  // Ouve continuamente por uma resposta do sensor
  receberRespostaDoSensor();
}

// =======================================================================
//                     4 - Funções de Comunicação
// =======================================================================

void inicializa_lora() {
  loraSerial.begin(9600);
  e22ttl.begin();

  // Lê a configuração atual para poder modificá-la
  ResponseStructContainer c = e22ttl.getConfiguration();
  Configuration configuration = *(Configuration*) c.data;
  
  // Modifica os parâmetros para ficarem compatíveis com a Pi
  configuration.ADDL = MY_ID;
  configuration.CHAN = CANAL_LORA;
  
  configuration.SPED.uartBaudRate = UART_BPS_9600;
  configuration.SPED.airDataRate = AIR_DATA_RATE;
  
  configuration.OPTION.transmissionPower = POWER_22;
  
  // CORREÇÃO IMPORTANTE: Parâmetros movidos para a sub-estrutura correta
  configuration.TRANSMISSION_MODE.fixedTransmission = FT_FIXED_TRANSMISSION;
  configuration.TRANSMISSION_MODE.enableRSSI = RSSI_ENABLED;

  // Grava a nova configuração no módulo
  ResponseStatus rs = e22ttl.setConfiguration(configuration, WRITE_CFG_PWR_DWN_SAVE);
  if (rs.code != E22_SUCCESS) {
    Serial.println("ERRO CRITICO: Falha ao salvar configuracao do LoRa! Verifique a fiacao.");
    while(1);
  }
  
  Serial.println("Modulo LoRa da Base configurado para 915 MHz.");
  delete (Configuration*)c.data;
}

void enviarComandoParaSensor() {
  Serial.print("\nEnviando chamado para o Sensor ID: ");
  Serial.println(ID_DO_SENSOR);

  // Prepara um pacote de comando simples (payload vazio)
  memset(PacoteDL, 0, TAMANHO_PACOTE); // Limpa o pacote
  PacoteDL[RECEIVER_ID] = ID_DO_SENSOR; // Destinatário é a Pi
  PacoteDL[TRANSMITTER_ID] = MY_ID;     // Remetente sou eu

  // Envia o pacote de chamada
  e22ttl.sendFixedMessage(0, ID_DO_SENSOR, CANAL_LORA, PacoteDL, TAMANHO_PACOTE);
}

void receberRespostaDoSensor() {
  // Verifica se o módulo LoRa tem dados a serem lidos
  if (e22ttl.available() > 1) { 
    ResponseContainer rc = e22ttl.receiveMessageRSSI();
    
    // Se a recepção foi bem-sucedida...
    if (rc.status.code == E22_SUCCESS) {
      // E o tamanho do pacote está correto...
      if (rc.data.length() >= TAMANHO_PACOTE) {
        // Copia os dados para nosso buffer global
        memcpy(PacoteUL, rc.data.c_str(), TAMANHO_PACOTE);
        
        // E o pacote foi realmente enviado pela Pi e era para mim...
        if (PacoteUL[TRANSMITTER_ID] == ID_DO_SENSOR && PacoteUL[RECEIVER_ID] == MY_ID) {
          // Imprime o conteúdo do pacote recebido
          imprimirRespostaDoSensor(rc.rssi);
        }
      }
    }
  }
}

void imprimirRespostaDoSensor(int rssi) {
  // Esta função imprime os dados recebidos da Pi no Monitor Serial
  Serial.println("---------------------------------------");
  Serial.println(">>> RESPOSTA RECEBIDA DA RASPBERRY PI <<<");
  Serial.print("RSSI (Qualidade do Sinal): ");
  Serial.print(rssi);
  Serial.println(" dBm");

  unsigned int uplink_counter = (PacoteUL[UL_COUNTER_MSB] << 8) | PacoteUL[UL_COUNTER_LSB];
  Serial.print("Contador de Pacotes da Pi: ");
  Serial.println(uplink_counter);

  Serial.println("Conteudo do Pacote (Hexadecimal):");
  for (int i=0; i < TAMANHO_PACOTE; i++) {
    if (PacoteUL[i] < 0x10) Serial.print("0"); // Adiciona zero à esquerda
    Serial.print(PacoteUL[i], HEX);
    Serial.print(" ");
    if ((i + 1) % 16 == 0) Serial.println(); // Quebra a linha a cada 16 bytes
  }
  Serial.println("\n---------------------------------------");
}