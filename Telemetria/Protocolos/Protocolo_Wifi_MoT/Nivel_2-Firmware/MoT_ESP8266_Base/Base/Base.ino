#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

// --- CONFIGURE OS DADOS DA SUA REDE DO CELULAR AQUI ---
const char* ssid = "FSAE Unicamp"; 
const char* password = "fsae2024"; 

// --- MUDANÇA: Usamos o nome mDNS em vez do IP fixo ---
const char* serverName = "raspberrypi.local"; 
const int serverPort = 4210;
const int localPort = 4210;

#define TAMANHO_PACOTE 52
#define INTERVALO_PING 2000

// IDs
#define PI_ID 100
#define ESP_ID 1

// Mapeamento
#define RSSI_UPLINK 0
#define RECEIVER_ID 8
#define TRANSMITTER_ID 10

// --- Variáveis Globais ---
WiFiUDP udp;
byte pacote_envio[TAMANHO_PACOTE];
byte pacote_recebido[TAMANHO_PACOTE];
unsigned long tempo_anterior = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("\n--- Cliente MoT WiFi (ESP8266) ---");

  // Conecta ao WiFi do celular
  WiFi.begin(ssid, password);
  Serial.print("Conectando a ");
  Serial.print(ssid);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConectado!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  udp.begin(localPort);
  Serial.println("UDP iniciado.");
}

void loop() {
  unsigned long tempo_atual = millis();

  if (tempo_atual - tempo_anterior >= INTERVALO_PING) {
    tempo_anterior = tempo_atual;

    // Monta o pacote de ping
    memset(pacote_envio, 0, TAMANHO_PACOTE);
    pacote_envio[RECEIVER_ID] = PI_ID;
    pacote_envio[TRANSMITTER_ID] = ESP_ID;
    
    // --- MUDANÇA: Envia o pacote usando o NOME do servidor ---
    // O ESP8266 resolve o IP automaticamente via mDNS
    udp.beginPacket(serverName, serverPort); 
    udp.write(pacote_envio, TAMANHO_PACOTE);
    udp.endPacket();

    Serial.print("\nPacote de PING enviado para ");
    Serial.println(serverName);
  }

  // Ouve por uma resposta
  int packetSize = udp.parsePacket();
  if (packetSize) {
    long downlink_rssi = WiFi.RSSI();
    udp.read(pacote_recebido, TAMANHO_PACOTE);
    
    short uplink_rssi;
    memcpy(&uplink_rssi, &pacote_recebido[RSSI_UPLINK], sizeof(uplink_rssi));

    Serial.println(">>> RESPOSTA RECEBIDA <<<");
    Serial.print("   RSSI de Subida (medido pela Pi):   ");
    Serial.print(uplink_rssi);
    Serial.println(" dBm");
    Serial.print("   RSSI de Descida (medido pelo ESP): ");
    Serial.print(downlink_rssi);
    Serial.println(" dBm");
  }
}