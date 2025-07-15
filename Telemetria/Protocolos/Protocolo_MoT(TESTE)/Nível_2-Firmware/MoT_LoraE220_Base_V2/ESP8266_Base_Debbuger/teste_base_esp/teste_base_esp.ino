#include <SoftwareSerial.h>

// Pinos
#define LORA_TX_PIN D3   // GPIO13
#define LORA_RX_PIN D4   // GPIO12
#define PIN_AUX D5       // GPIO14
#define PIN_M0  D7       // GPIO5
#define PIN_M1  D6       // GPIO4  <-- ATENÇÃO: Corrigi o pino para D2/GPIO4 para ser único.

SoftwareSerial loraSerial(LORA_RX_PIN, LORA_TX_PIN); // RX, TX

// Função para definir o modo do módulo
void setLoraMode(int mode) {
  if (mode == 0) { // Modo Normal
    digitalWrite(PIN_M0, LOW);
    digitalWrite(PIN_M1, LOW);
    Serial.println("LoRa em MODO NORMAL.");
  } else if (mode == 2) { // Modo Configuração
    digitalWrite(PIN_M0, LOW);
    digitalWrite(PIN_M1, HIGH);
    Serial.println("LoRa em MODO CONFIGURACAO.");
  }
}

void setup() {
  Serial.begin(115200);
  while (!Serial) {};
  
  pinMode(PIN_M0, OUTPUT);
  pinMode(PIN_M1, OUTPUT);
  pinMode(PIN_AUX, INPUT);
  
  loraSerial.begin(9600); // A configuração é sempre feita a 9600 bps [cite: 327]

  Serial.println("\n--- CONFIGURANDO MODULO LORA (ESP8266) ---");

  // 1. Entra no modo de configuração
  setLoraMode(2);
  delay(100); // Pequena pausa para o módulo trocar de modo

  // 2. Monta o pacote de configuração baseado no manual
  // Comando: C0 (Salvar) + Endereço Inicial (00h) + Tamanho (6 bytes) + Parâmetros...
  byte config_packet[] = {
    0xC0, // Comando: Salvar configuração permanentemente [cite: 328]
    0x00, // Endereço inicial do registro: 00H [cite: 328]
    0x06, // Tamanho: Vamos configurar 6 bytes [cite: 328]
    0x00, // ADDH: Endereço do módulo (Byte alto) = 0 [cite: 335]
    0x00, // ADDL: Endereço do módulo (Byte baixo) = 0 [cite: 335]
    0x00, // NETID: ID da Rede = 0 [cite: 335]
    0x62, // REG0: UART 9600bps, Air Rate 2.4kbps [cite: 339]
    0x00, // REG1: Potência 30dBm (padrão) [cite: 339]
    0x41  // REG2: Canal para 915 MHz [cite: 339]
  };

  // 3. Envia o pacote de configuração pela serial
  loraSerial.write(config_packet, sizeof(config_packet));
  Serial.println("Pacote de configuracao enviado.");
  
  delay(2000); // Espera o módulo processar e salvar

  // 4. Volta para o modo normal
  setLoraMode(0);
  delay(200);

  Serial.println("--- CONFIGURACAO CONCLUIDA ---");
  Serial.println("ESP8266 pronto para enviar LoRa!");
}

void loop() {
  String mensagem = "Ola Raspberry Pi, aqui eh a Base ESP8266!";
  
  // Usar write em vez de println para não enviar caracteres extras de nova linha
  loraSerial.write(mensagem.c_str()); 
  
  Serial.print("Mensagem enviada: ");
  Serial.println(mensagem);
  
  delay(5000); // Envia a cada 5 segundos
}