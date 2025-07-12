#ifndef BIBLIOTECAS_H
#define BIBLIOTECAS_H

#include "Arduino.h"
#include "LoRa_E22.h" // Usando a biblioteca que você especificou
#include <SoftwareSerial.h>

// =======================================================================
//                    Configurações Gerais do Projeto
// =======================================================================
#define MY_ID              10      // ID desta Base
#define ID_DO_SENSOR       1       // ID do nó sensor que iremos chamar
#define TAXA_SERIAL        115200  // Taxa de comunicação com o PC
#define TAMANHO_PACOTE     52
#define INTERVALO_POLL     5000    // Chamar o sensor a cada 5 segundos (5000 ms)

// --- CONFIGURAÇÕES DO RÁDIO E22 ---
#define CANAL_LORA         65      // Canal para 915 MHz (deve ser o mesmo do sensor)

// =======================================================================
//                  Definições dos Pinos para ESP8266
// =======================================================================
#define LORA_RX_PIN        D6      // GPIO12 (Conectado ao pino TX do módulo E22)
#define LORA_TX_PIN        D5      // GPIO14 (Conectado ao pino RX do módulo E22)
#define LORA_AUX_PIN       D7      // GPIO13
#define LORA_M0_PIN        D1      // GPIO5
#define LORA_M1_PIN        D2      // GPIO4

// =======================================================================
//                  Instanciação dos Objetos
// =======================================================================
SoftwareSerial loraSerial(LORA_RX_PIN, LORA_TX_PIN);
LoRa_E22 e22ttl(&loraSerial, LORA_AUX_PIN, LORA_M0_PIN, LORA_M1_PIN);

// =======================================================================
//                  Variáveis Globais
// =======================================================================
byte PacoteDL[TAMANHO_PACOTE]; // Pacote para enviar ao sensor (Downlink)
byte PacoteUL[TAMANHO_PACOTE]; // Pacote recebido do sensor (Uplink)
int RSSI_dBm_UL, RSSI_UL, LQI_UL;
unsigned long ultimoPoll = 0; // Para controlar o tempo de chamada

// =======================================================================
//                Enumeração do Pacote
// =======================================================================
enum bytes_do_pacote{
  RSSI_UPLINK   = 0, LQI_UPLINK    = 1, RSSI_DOWNLINK = 2, LQI_DOWNLINK  = 3,
  MAC_COUNTER_MSB = 4, MAC_COUNTER_LSB = 5, MAC3 = 6, MAC4 = 7,
  RECEIVER_ID     = 8, NET2            = 9, TRANSMITTER_ID  = 10, NET4 = 11,
  DL_COUNTER_MSB = 12, DL_COUNTER_LSB = 13, UL_COUNTER_MSB = 14, UL_COUNTER_LSB = 15,
  Data1 = 16, Data2 = 17, Data3 = 18, Data4 = 19,
};

#endif // BIBLIOTECAS_H