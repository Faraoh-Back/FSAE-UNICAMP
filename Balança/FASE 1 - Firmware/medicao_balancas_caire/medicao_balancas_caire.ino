#include <HX711.h>

// Definição do número de balanças
#define NUM_BALANCAS 4

// Definições de pinos DT e SCK para cada balança
const int pinDT[NUM_BALANCAS] = {2, 4, 6, 8};
const int pinSCK[NUM_BALANCAS] = {3, 5, 7, 9};

// Array de objetos HX711 para as balanças
HX711 scales[NUM_BALANCAS];

// Array para armazenar as medidas de cada balança
float medidas[NUM_BALANCAS];

// Array para armazenar as escalas de cada balança
float escalas[NUM_BALANCAS] = {-28061, -28033, -27846, -28246}; // Defina as escalas desejadas aqui

// Variáveis para acompanhar o tempo
unsigned long tempoInicial = 0;
unsigned long tempoAtual = 0;

void setup() {
  Serial.begin(57600);

  // Configuração e taragem das balanças
  Serial.print("<Balança ");
  for (int i = 0; i < NUM_BALANCAS; i++) {
    scales[i].begin(pinDT[i], pinSCK[i]);
    scales[i].set_scale(escalas[i]); // Definindo a escala individualmente para cada balança
    delay(2000);
    scales[i].tare();

    // Definindo mensagens personalizadas para cada balança
    switch(i) {
      case 0:
        Serial.print("FL/1");
        break;
      case 1:
        Serial.print("FR/2");
        break;
      case 2:
        Serial.print("RL/3");
        break;
      case 3:
        Serial.print("RR/4");
        break;
    }

    Serial.print(" zerada");
    if (i < NUM_BALANCAS-1) Serial.print("; ");

  }
  Serial.println(">");

  // Inicializando o tempo
  tempoInicial = millis();
}

void loop() {
  // Verificando se passaram 10 segundos
  tempoAtual = millis();
  if (tempoAtual - tempoInicial >= 10000) {
    // Calculando o valor médio das balanças nos últimos 10 segundos
    float media[NUM_BALANCAS] = {0}; // Array para armazenar as médias de cada balança
    int contagem[NUM_BALANCAS] = {0}; // Array para armazenar a contagem de medidas de cada balança

    // Percorrendo as medidas das balanças nos últimos 10 segundos
    for (int i = 0; i < NUM_BALANCAS; i++) {
      media[i] += medidas[i];
      contagem[i]++;
    }

    // Calculando as médias de cada balança
    for (int i = 0; i < NUM_BALANCAS; i++) {
      if (contagem[i] != 0) {
        media[i] /= contagem[i];
      }
    }

    // Imprimindo o valor médio das balanças
    Serial.print("<MEDIA; ");
    for (int i = 0; i < NUM_BALANCAS; i++) {
/*
      // Definindo mensagens personalizadas para cada balança
      switch(i) {
        case 0:
          Serial.print("FL/1:");
          break;
        case 1:
          Serial.print("FR/2:");
          break;
        case 2:
          Serial.print("RL/3:");
          break;
        case 3:
          Serial.print("RR/4:");
          break;
      }*/
      Serial.print(media[i], 3);
      if (i < NUM_BALANCAS-1) Serial.print(";");
    }
    Serial.println(">");

    // Reinicializando o tempo
    tempoInicial = millis();
  }

  // Obtendo as medidas de cada balança
  Serial.print("<LEITURA; ");
  for (int i = 0; i < NUM_BALANCAS; i++) {
    medidas[i] = scales[i].get_units(5);
    
    /*
    // Definindo mensagens personalizadas para cada balança
    switch(i) {
      case 0:
        Serial.print("FL/1:");
        break;
      case 1:
        Serial.print("FR/2:");
        break;
      case 2:
        Serial.print("RL/3:");
        break;
      case 3:
        Serial.print("RR/4:");
        break;
    }*/

    Serial.print(medidas[i], 3);
    if (i < NUM_BALANCAS-1) Serial.print(";");
  }
  Serial.println(">");

  // Desligando e ligando os sensores para evitar erros
  for (int i = 0; i < NUM_BALANCAS; i++) {
    scales[i].power_down();
  }
  delay(1000);
  for (int i = 0; i < NUM_BALANCAS; i++) {
    scales[i].power_up();
  }
}