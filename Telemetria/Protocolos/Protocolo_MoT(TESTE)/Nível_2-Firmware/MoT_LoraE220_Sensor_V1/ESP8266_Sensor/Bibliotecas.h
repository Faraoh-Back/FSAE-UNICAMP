#ifndef BIBLIOTECAS_H
#define BIBLIOTECAS_H

#include "Arduino.h"
#include "LoRa_E22.h" // A biblioteca que já instalamos
#include <SoftwareSerial.h>

// =======================================================================
//                    Configurações Gerais do Nó Sensor
// =======================================================================
// IDs DEVEM ser o inverso do que está na Base
#define MY_ID              1       // ID deste Nó Sensor
#define ID_DA_BASE         10      // ID da Base para qual ele vai responder
#define TAXA_SERIAL        115200  // Taxa para debug no Monitor Serial
#define TAMANHO_PACOTE     52

// --- CONFIGURAÇÕES DO RÁDIO E22 ---
// Devem ser compatíveis com a configuração da Base
#define CANAL_LORA         65      // Canal para 915 MHz
#define AIR_DATA_RATE      AIR_DATA_RATE_010_24 // 2.4kbps
#define POTENCIA_TX        POWER_22 // 22dBm

// =======================================================================
//                  Definições dos Pinos para ESP8266
// =======================================================================
// Usando a mesma pinagem que definimos para a Base, para facilitar
#define LORA_RX_PIN        D5      // GPIO14 (Conectado ao pino TX do módulo E22)
#define LORA_TX_PIN        D6      // GPIO12 (Conectado ao pino RX do módulo E22)
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
byte PacoteDL[TAMANHO_PACOTE]; // Pacote recebido da Base (Downlink)
byte PacoteUL[TAMANHO_PACOTE]; // Pacote a ser enviado para a Base (Uplink)
int contadorUL = 0;
int RSSI_dBm_DL, RSSI_DL, LQI_DL;

// =======================================================================
//                Enumeração do Pacote (Idêntica à da Base)
// =======================================================================
enum bytes_do_pacote{
  RSSI_UPLINK   = 0, LQI_UPLINK    = 1, RSSI_DOWNLINK = 2, LQI_DOWNLINK  = 3,
  MAC_COUNTER_MSB = 4, MAC_COUNTER_LSB = 5, MAC3 = 6, MAC4 = 7,
  RECEIVER_ID     = 8, NET2            = 9, TRANSMITTER_ID  = 10, NET4 = 11,
  DL_COUNTER_MSB = 12, DL_COUNTER_LSB = 13, UL_COUNTER_MSB = 14, UL_COUNTER_LSB = 15,
  // O resto do pacote pode ser usado para dados de sensores
  Data1 = 16, Data2 = 17, Data3 = 18, Data4 = 19,
};

#endif // BIBLIOTECAS_H