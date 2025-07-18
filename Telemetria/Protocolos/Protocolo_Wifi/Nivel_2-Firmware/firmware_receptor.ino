// ESP8266_Cliente_WiFi.ino
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>

// --- CONFIGURE AQUI ---
const char* ssid = "FSAE_Telemetria"; // O nome da rede WiFi que você criou na Pi
const char* password = "sua_senha_aqui"; // A senha da rede
const char* server_ip = "192.168.4.1"; // IP padrão da Pi em modo AP
const int server_port = 8000;

void setup() {
  Serial.begin(115200);
  delay(10);

  Serial.println("\n--- Cliente de Telemetria WiFi (ESP8266) ---");
  
  // Conectando ao WiFi
  Serial.print("Conectando a ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi conectado!");
  Serial.print("Endereco IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Espera 5 segundos entre cada requisição
  delay(5000);

  WiFiClient client;
  HTTPClient http;

  // Monta a URL para requisitar os dados
  String serverPath = "http://" + String(server_ip) + ":" + String(server_port) + "/data";
  
  Serial.print("Requisitando dados de: ");
  Serial.println(serverPath);

  // Inicia a requisição HTTP
  if (http.begin(client, serverPath)) {
    int httpCode = http.GET();

    if (httpCode > 0) { // Verifica se a requisição foi bem-sucedida
      if (httpCode == HTTP_CODE_OK) {
        String payload = http.getString();
        Serial.println("Dados recebidos:");
        Serial.println(payload);
        // Aqui você pode adicionar a lógica para processar a string CSV recebida
      }
    } else {
      Serial.printf("Falha na requisicao HTTP, erro: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end(); // Libera os recursos
  } else {
    Serial.println("Nao foi possivel conectar ao servidor.");
  }
}