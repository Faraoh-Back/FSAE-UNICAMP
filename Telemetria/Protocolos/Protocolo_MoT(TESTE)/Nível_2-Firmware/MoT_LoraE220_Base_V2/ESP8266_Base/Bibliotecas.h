#ifndef BIBLIOTECAS_H
#define BIBLIOTECAS_H
// --- MUDANÇA: SoftwareSerial agora é necessária para o ESP8266 ---
#include <SoftwareSerial.h>

//#include <RH_RF95.h>
#include "Arduino.h"
#include "LoRa_E220.h"

#define MY_ID 1 
#define TAXA_SERIAL 115200
#define TAMANHO_PACOTE 52
#define FREQUENCY_IN_MHZ 915.0

// --- MUDANÇA: Novos pinos para o ESP8266 (NodeMCU/Wemos) ---
#define LORA_RX_PIN      12      // GPIO12 (D6)
#define LORA_TX_PIN      13      // GPIO13 (D7)
#define LORA_AUX_PIN     4       // GPIO4  (D2)
#define LORA_M0_PIN      5       // GPIO5  (D1)
#define LORA_M1_PIN      14      // GPIO14 (D5)

// --- MUDANÇA: Criar um objeto SoftwareSerial para a comunicação LoRa ---
SoftwareSerial loraSerial(LORA_RX_PIN, LORA_TX_PIN);

// --- MUDANÇA: Inicializar o LoRa usando o objeto loraSerial ---
LoRa_E220 e220ttl(&loraSerial, LORA_AUX_PIN, LORA_M0_PIN, LORA_M1_PIN);

//#define ShowSerial Serial

// O resto do arquivo permanece o mesmo...
byte PacoteDL[TAMANHO_PACOTE];
byte PacoteUL[TAMANHO_PACOTE];
int contadorUL;
int contadorDL;
int RSSI_dBm_UL, RSSI_UL, LQI_UL;

enum bytes_do_pacote{
  /* ... (o enum continua igual) ... */
  RSSI_UPLINK   = 0,
  LQI_UPLINK    = 1,
  RSSI_DOWNLINK = 2,
  LQI_DOWNLINK  = 3,
  MAC_COUNTER_MSB = 4, 
  MAC_COUNTER_LSB = 5,
  MAC3 = 6,
  MAC4 = 7,
  RECEIVER_ID     = 8,
  NET2            = 9,
  TRANSMITTER_ID  = 10,
  NET4            = 11,
  DL_COUNTER_MSB = 12,
  DL_COUNTER_LSB = 13,
  UL_COUNTER_MSB = 14,
  UL_COUNTER_LSB = 15,
  APP1 = 16,
  APP2 = 17,
  APP3 = 18,
  APP4 = 19,
  APP5 = 20,
  APP6 = 21,
  APP7 = 22,
  APP8 = 23,
  APP9 = 24,
  APP10 = 25,
  APP11 = 26,
  APP12 = 27,
  APP13 = 28, 
  APP14 = 29,
  APP15 = 30,
  APP16 = 31,
  APP17 = 32,
  APP18 = 33,
  APP19 = 34,
  APP20 = 35,
  APP21 = 36,
  APP22 = 37,
  APP23 = 38,
  APP24 = 39,
  APP25 = 40,
  APP26 = 41,
  APP27 = 42,
  APP28 = 43,
  APP29 = 44,
  APP30 = 45,
  APP31 = 46,
  APP32 = 47,
  APP33 = 48,
  APP34 = 49,
  APP35 = 50,
  APP36 = 51,
};

#endif