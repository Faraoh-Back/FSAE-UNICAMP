#ifndef BIBLIOTECAS_H
#define BIBLIOTECAS_H

#include "Arduino.h"
#include "LoRa_E22.h" // <-- MUDANÇA: Usando a biblioteca que você especificou
#include <SoftwareSerial.h>

// =======================================================================
//                    Configurações Gerais da Base
// =======================================================================
// IDs para comunicação com a Raspberry Pi
#define MY_ID              1   // Endereço de Hardware e Lógico desta Base (Professor)
#define SENSOR_ID          100 // Endereço de Hardware e Lógico do Sensor (Pi/Aluno)

#define TAXA_SERIAL        115200 // Comunicação com o PC
#define TAMANHO_PACOTE     52
#define INTERVALO_POLL     5000   // Chamar o sensor a cada 5 segundos

// =======================================================================
//                  Definições dos Pinos para ESP8266
// =======================================================================
// Usando pinos comuns e seguros para o NodeMCU ESP8266
#define LORA_RX_PIN        D5      // GPIO14 (Conectado ao pino TX do módulo E22)
#define LORA_TX_PIN        D6      // GPIO12 (Conectado ao pino RX do módulo E22)
#define LORA_AUX_PIN       D7      // GPIO13
#define LORA_M0_PIN        D1      // GPIO5
#define LORA_M1_PIN        D2      // GPIO4

// =======================================================================
//                  Instanciação dos Objetos
// =======================================================================
// A biblioteca LoRa_E22 também funciona melhor com SoftwareSerial no ESP8266
SoftwareSerial loraSerial(LORA_RX_PIN, LORA_TX_PIN);

// O construtor da LoRa_E22 é idêntico ao da E220
LoRa_E22 e22ttl(&loraSerial, LORA_AUX_PIN, LORA_M0_PIN, LORA_M1_PIN);

// =======================================================================
//                  Variáveis Globais e Enum
// =======================================================================
// (Esta seção é mantida idêntica ao seu código original)
byte PacoteDL[TAMANHO_PACOTE];
byte PacoteUL[TAMANHO_PACOTE];
int contadorUL = 0;
int contadorDL = 0;
int RSSI_dBm_UL, RSSI_UL, LQI_UL;

enum bytes_do_pacote{
  RSSI_UPLINK   = 0, LQI_UPLINK    = 1, RSSI_DOWNLINK = 2, LQI_DOWNLINK  = 3,
  MAC_COUNTER_MSB = 4, MAC_COUNTER_LSB = 5, MAC3 = 6, MAC4 = 7,
  RECEIVER_ID     = 8, NET2            = 9, TRANSMITTER_ID  = 10, NET4 = 11,
  DL_COUNTER_MSB = 12, DL_COUNTER_LSB = 13, UL_COUNTER_MSB = 14, UL_COUNTER_LSB = 15,
  APP1 = 16, APP2 = 17, APP3 = 18, APP4 = 19, APP5 = 20, APP6 = 21, APP7 = 22,
  APP8 = 23, APP9 = 24, APP10 = 25, APP11 = 26, APP12 = 27, APP13 = 28, APP14 = 29,
  APP15 = 30, APP16 = 31, APP17 = 32, APP18 = 33, APP19 = 34, APP20 = 35, APP21 = 36,
  APP22 = 37, APP23 = 38, APP24 = 39, APP25 = 40, APP26 = 41, APP27 = 42, APP28 = 43,
  APP29 = 44, APP30 = 45, APP31 = 46, APP32 = 47, APP33 = 48, APP34 = 49, APP35 = 50,
  APP36 = 51,
};

#endif // BIBLIOTECAS_H