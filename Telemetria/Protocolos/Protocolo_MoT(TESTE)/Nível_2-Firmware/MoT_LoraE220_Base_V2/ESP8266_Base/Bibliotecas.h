#ifndef BIBLIOTECAS_H
#define BIBLIOTECAS_H

#include "Arduino.h"
// Usaremos a biblioteca LoRa_E220, que é a versão mais atual e estável
// Se você instalou pelo Gerenciador de Bibliotecas, o nome do arquivo .h é este.
#include "LoRa_E220.h"
#include <SoftwareSerial.h>

// =======================================================================
//                    Configurações Gerais do Projeto
// =======================================================================
#define MY_ID              10      // ID desta Base
#define ID_DO_SENSOR       100     // ID do nó sensor (Raspberry Pi) que iremos chamar
#define TAXA_SERIAL        115200  // Taxa de comunicação com o PC para debug
#define TAMANHO_PACOTE     52
#define INTERVALO_POLL     5000    // Chamar o sensor a cada 5 segundos (5000 ms)

// --- CONFIGURAÇÕES DO RÁDIO E22 ---
#define CANAL_LORA         65      // Canal para 915 MHz (deve ser o mesmo da Pi)
// Taxa de transmissão pelo ar. Deve ser a mesma configurada na Pi.
#define AIR_DATA_RATE      AIR_DATA_RATE_2400_8N1

// =======================================================================
//                  Definições dos Pinos para ESP8266
// =======================================================================
#define LORA_RX_PIN        D5      // GPIO14 (Conectado ao pino TX do módulo E22)
#define LORA_TX_PIN        D6      // GPIO12 (Conectado ao pino RX do módulo E22)
#define LORA_AUX_PIN       D7      // GPIO13
#define LORA_M0_PIN        D1      // GPIO5
#define LORA_M1_PIN        D2      // GPIO4

// =======================================================================
//                  Instanciação dos Objetos
// =======================================================================
SoftwareSerial loraSerial(LORA_RX_PIN, LORA_TX_PIN);
LoRa_E220 e22ttl(&loraSerial, LORA_AUX_PIN, LORA_M0_PIN, LORA_M1_PIN);

// =======================================================================
//                  Variáveis Globais
// =======================================================================
byte PacoteDL[TAMANHO_PACOTE]; // Pacote para enviar ao sensor (Downlink)
byte PacoteUL[TAMANHO_PACOTE]; // Pacote recebido do sensor (Uplink)
unsigned long ultimoPoll = 0; // Para controlar o tempo de chamada

// =======================================================================
//                Enumeração do Pacote (para referência)
// =======================================================================
enum bytes_do_pacote{
  RSSI_UPLINK   = 0, LQI_UPLINK    = 1, RSSI_DOWNLINK = 2, LQI_DOWNLINK  = 3,
  RECEIVER_ID     = 8, TRANSMITTER_ID  = 10,
  UL_COUNTER_MSB = 14, UL_COUNTER_LSB = 15,
};

#endif // BIBLIOTECAS_H