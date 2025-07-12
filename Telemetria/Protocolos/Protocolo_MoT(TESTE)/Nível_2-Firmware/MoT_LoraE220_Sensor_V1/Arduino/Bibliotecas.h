#ifndef BIBLIOTECAS_H
#define BIBLIOTECAS_H

#include "Arduino.h"
#include <SoftwareSerial.h>
#include "LoRa_E22.h" // <-- Incluindo a biblioteca correta

// --- CONFIGURAÇÕES GERAIS ---
#define MY_ID              1
#define ID_DA_BASE         10
#define TAXA_SERIAL        9600
#define TAMANHO_PACOTE     52

// --- PINOS DO ARDUINO (Uno, Nano, etc.) ---
#define LORA_RX_PIN        2
#define LORA_TX_PIN        3
#define LORA_AUX_PIN       4
#define LORA_M0_PIN        5
#define LORA_M1_PIN        6

// --- OBJETOS GLOBAIS ---
SoftwareSerial loraSerial(LORA_RX_PIN, LORA_TX_PIN);
LoRa_E22 e22ttl(&loraSerial, LORA_AUX_PIN, LORA_M0_PIN, LORA_M1_PIN);

// --- VARIÁVEIS GLOBAIS ---
byte PacoteDL[TAMANHO_PACOTE];
byte PacoteUL[TAMANHO_PACOTE];
int contadorUL = 0;
int RSSI_dBm_DL, RSSI_DL, LQI_DL;

// --- ESTRUTURA DO PACOTE ---
enum bytes_do_pacote{
  RSSI_UPLINK   = 0, LQI_UPLINK    = 1, RSSI_DOWNLINK = 2, LQI_DOWNLINK  = 3,
  MAC_COUNTER_MSB = 4, MAC_COUNTER_LSB = 5, MAC3 = 6, MAC4 = 7,
  RECEIVER_ID     = 8, NET2            = 9, TRANSMITTER_ID  = 10, NET4 = 11,
  DL_COUNTER_MSB = 12, DL_COUNTER_LSB = 13, UL_COUNTER_MSB = 14, UL_COUNTER_LSB = 15,
  APP1 = 16,
};

#endif // BIBLIOTECAS_H