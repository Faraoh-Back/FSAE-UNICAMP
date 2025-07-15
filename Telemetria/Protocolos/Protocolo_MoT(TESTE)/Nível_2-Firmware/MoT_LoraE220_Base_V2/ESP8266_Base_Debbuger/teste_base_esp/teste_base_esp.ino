#include <SoftwareSerial.h>

// Definindo os pinos conforme informado
#define LORA_TX D3   // GPIO0, TX do ESP8266 vai no RX do E22
#define LORA_RX D4   // GPIO2, RX do ESP8266 vai no TX do E22
#define PIN_AUX D5   // GPIO14
#define PIN_M0  D7   // GPIO13
#define PIN_M1  D6   // GPIO12

SoftwareSerial loraSerial(LORA_RX, LORA_TX); // RX, TX

void setNormalMode() {
  digitalWrite(PIN_M0, LOW);
  digitalWrite(PIN_M1, LOW);
}

void setup() {
  Serial.begin(115200);
  loraSerial.begin(9600); // padrão do E22
  pinMode(PIN_AUX, INPUT);
  pinMode(PIN_M0, OUTPUT);
  pinMode(PIN_M1, OUTPUT);

  setNormalMode(); // Modo normal de operação
  delay(100);

  Serial.println("ESP8266 pronto para enviar LoRa!");
}

void loop() {
  String mensagem = "Ola Raspberry!";
  loraSerial.println(mensagem);
  Serial.println("Mensagem enviada: " + mensagem);
  delay(5000);
}