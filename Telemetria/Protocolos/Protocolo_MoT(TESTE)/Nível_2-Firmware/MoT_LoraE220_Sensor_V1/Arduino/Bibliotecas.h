// #include <RH_RF95.h>
// #include <SoftwareSerial.h>
#include "Arduino.h"
#include "LoRa_E220.h"

#define MY_ID 1 
#define TAXA_SERIAL 115200
#define TAMANHO_PACOTE 52
#define FREQUENCY_IN_MHZ 868.0
#define POWER_TX_DBM 5 
#define NO_SENSOR 0
#define TRANSCEPTOR_BORDA 1
#define MODO_DO_DISPOSITIVO NO_SENSOR
#define PINO_RX 1
#define PINO_TX 0

// ---------- Arduino pins --------------
LoRa_E220 e220ttl(4, 5, 3, 7, 6); // Arduino RX <-- e220 TX, Arduino TX --> e220 RX AUX/4 M0/5 M1/6 (Connections between Arduino and EByte E220)

// SoftwareSerial SSerial(PINO_RX, PINO_TX);
// #define COMSerial SSerial
#define ShowSerial Serial

// Se der erro na compilação inverter os comentários das duas linhas a seguir
//RH_RF95 rf95(COMSerial);
// RH_RF95<SoftwareSerial> rf95(COMSerial);

byte PacoteDL[TAMANHO_PACOTE];
byte PacoteUL[TAMANHO_PACOTE];
int contadorUL;
int contadorDL;
int RSSI_dBm_DL, RSSI_DL, LQI_DL;

enum bytes_do_pacote{
  /* Physical Layer */
  RSSI_UPLINK   = 0,
  LQI_UPLINK    = 1,
  RSSI_DOWNLINK = 2,
  LQI_DOWNLINK  = 3,

  /* MAC Layer */
  MAC_COUNTER_MSB = 4, 
  MAC_COUNTER_LSB = 5,
  MAC3 = 6,
  MAC4 = 7,

  /* Network Layer */
  RECEIVER_ID     = 8,
  NET2            = 9,
  TRANSMITTER_ID  = 10,
  NET4            = 11,

  /* Transport Layer */
  DL_COUNTER_MSB = 12,
  DL_COUNTER_LSB = 13,
  UL_COUNTER_MSB = 14,
  UL_COUNTER_LSB = 15,

  /* Application Layer */
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
