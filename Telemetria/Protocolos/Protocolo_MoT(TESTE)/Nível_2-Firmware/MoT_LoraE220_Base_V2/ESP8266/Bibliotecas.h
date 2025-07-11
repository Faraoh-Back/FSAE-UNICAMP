#ifndef BIBLIOTECAS_H
#define BIBLIOTECAS_H

#include "Arduino.h"
#include "LoRa_E220.h"
#include <SoftwareSerial.h> // Essencial para o ESP8266

// =======================================================================
//                    Configurações Gerais do Projeto
// =======================================================================
#define MY_ID 10
#define TAXA_SERIAL 115200 // Taxa de comunicação com o PC/Raspberry Pi
#define TAMANHO_PACOTE 52

// =======================================================================
//                  Definições dos Pinos para ESP8266
// =======================================================================
// Pinos do NodeMCU conforme a sua conexão
#define LORA_RX_PIN D5 // GPIO14
#define LORA_TX_PIN D6 // GPIO12
#define LORA_AUX_PIN D7 // GPIO13
#define LORA_M0_PIN D1 // GPIO5
#define LORA_M1_PIN D2 // GPIO4

// =======================================================================
//                  Instanciação dos Objetos LoRa
// =======================================================================
// 1. Cria uma porta serial de software para comunicar com o LoRa
SoftwareSerial loraSerial(LORA_RX_PIN, LORA_TX_PIN);

// 2. Cria o objeto LoRa, passando a porta serial e os pinos de controle
// Ordem: (ponteiro para a Serial, pino AUX, M0, M1)
LoRa_E220 e220ttl(&loraSerial, LORA_AUX_PIN, LORA_M0_PIN, LORA_M1_PIN);

// =======================================================================
//                  Variáveis Globais do Projeto
// =======================================================================
byte PacoteDL[TAMANHO_PACOTE]; // Pacote recebido via Serial (Downlink)
byte PacoteUL[TAMANHO_PACOTE]; // Pacote a ser enviado via Serial (Uplink)

int RSSI_dBm_UL; // RSSI do último pacote recebido do rádio
int RSSI_UL;     // RSSI convertido para o formato do seu protocolo
int LQI_UL;      // LQI (Link Quality Indicator)

// =======================================================================
//                Enumeração do Pacote (Mantido Idêntico)
// =======================================================================
enum bytes_do_pacote{
  /* Physical Layer */
  RSSI_UPLINK   = 0, LQI_UPLINK    = 1, RSSI_DOWNLINK = 2, LQI_DOWNLINK  = 3,
  /* MAC Layer */
  MAC_COUNTER_MSB = 4, MAC_COUNTER_LSB = 5, MAC3 = 6, MAC4 = 7,
  /* Network Layer */
  RECEIVER_ID     = 8, NET2            = 9, TRANSMITTER_ID  = 10, NET4            = 11,
  /* Transport Layer */
  DL_COUNTER_MSB = 12, DL_COUNTER_LSB = 13, UL_COUNTER_MSB = 14, UL_COUNTER_LSB = 15,
  /* Application Layer */
  APP1 = 16, APP2 = 17, APP3 = 18, APP4 = 19, APP5 = 20, APP6 = 21, APP7 = 22, APP8 = 23,
  APP9 = 24, APP10 = 25, APP11 = 26, APP12 = 27, APP13 = 28, APP14 = 29, APP15 = 30,
  APP16 = 31, APP17 = 32, APP18 = 33, APP19 = 34, APP20 = 35, APP21 = 36, APP22 = 37,
  APP23 = 38, APP24 = 39, APP25 = 40, APP26 = 41, APP27 = 42, APP28 = 43, APP29 = 44,
  APP30 = 45, APP31 = 46, APP32 = 47, APP33 = 48, APP34 = 49, APP35 = 50, APP36 = 51,
};

#endif