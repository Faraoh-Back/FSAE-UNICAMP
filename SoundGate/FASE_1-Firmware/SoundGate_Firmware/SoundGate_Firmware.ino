/*
 * SoundGate - Firmware Simplificado para Dashboard
 * Descrição: Este código mede o tempo de voltas de um carro usando um
 * sensor ultrassônico e envia os dados formatados via serial.
 * A primeira detecção do carro inicia a contagem de tempo e registra a primeira volta.
 */

// Inclui a biblioteca do sensor (necessária no mesmo diretório ou na pasta de bibliotecas do Arduino)
#include "Ultrasonic.h" // Certifique-se que os arquivos Ultrasonic.h e Ultrasonic.cpp estão disponíveis

// --- Configurações ---
#define PINO_TRG  5 // Pino Trigger do sensor ultrassônico
#define PINO_ECHO 6 // Pino Echo do sensor ultrassônico

// Faixa de distância em cm para detectar o carro
const float DISTANCIA_MINIMA = 20.0;
const float DISTANCIA_MAXIMA = 100.0;

// Tempo de "debounce" em milissegundos para evitar dupla contagem na mesma passagem
const unsigned long TEMPO_DEBOUNCE = 3000;

// --- Variáveis Globais ---
Ultrasonic ultrasonic(PINO_TRG, PINO_ECHO);

int voltas = 0;
unsigned long tempoInicial = 0;
unsigned long tempoDaUltimaVolta = 0;
unsigned long tempoUltimaDeteccao = 0;

void setup() {
  Serial.begin(9600);
  
  // Mensagens iniciais
  Serial.println("FSAE - SoundGate");
  Serial.println("Aguardando passagem do carro...");
  
  // Cabeçalho para CSV
  Serial.println("Volta,Distancia,Tempo de Volta,Tempo Total");
}

void loop() {
  // Faz a leitura da distância
  long microsec = ultrasonic.timing();
  float distanciaCm = ultrasonic.convert(microsec, Ultrasonic::CM);
  
  // Verifica se o carro está na área de detecção
  if (distanciaCm > DISTANCIA_MINIMA && distanciaCm < DISTANCIA_MAXIMA) {
    
    // Verifica se o tempo de debounce já passou desde a última detecção
    if (millis() - tempoUltimaDeteccao > TEMPO_DEBOUNCE) {
      
      unsigned long tempoAtual = millis();
      
      // Se for a primeira volta, inicializa os contadores de tempo
      if (voltas == 0) {
        tempoInicial = tempoAtual;
        tempoDaUltimaVolta = tempoAtual;
        Serial.println("Carro identificado. Iniciando cronometragem...");
      }
      
      // Calcula os tempos
      unsigned long tempoDeVoltaMs = tempoAtual - tempoDaUltimaVolta;
      unsigned long tempoTotalMs = tempoAtual - tempoInicial;
      
      // --- Impressão dos Dados no formato CSV ---
      
      // Volta
      Serial.print(voltas);
      Serial.print(",");
      
      // Distância
      Serial.print(distanciaCm);
      Serial.print(" cm");
      Serial.print(",");
      
      // Tempo de Volta (em segundos com 3 casas decimais)
      Serial.print(tempoDeVoltaMs / 1000);
      Serial.print(".");
      if (tempoDeVoltaMs % 1000 < 100) Serial.print("0");
      if (tempoDeVoltaMs % 1000 < 10) Serial.print("0");
      Serial.print(tempoDeVoltaMs % 1000);
      Serial.print(" seg");
      Serial.print(",");
      
      // Tempo Total (formato X min Y seg)
      Serial.print(tempoTotalMs / 1000);
      Serial.print(".");
      if (tempoTotalMs % 1000 < 100) Serial.print("0");
      if (tempoTotalMs % 1000 < 10) Serial.print("0");
      Serial.print(tempoTotalMs % 1000);
      Serial.println(" seg");
      
      // Atualiza os marcadores de tempo para a próxima volta
      tempoDaUltimaVolta = tempoAtual;
      tempoUltimaDeteccao = tempoAtual;

      // Incrementa o número de voltas
      voltas++;
    }
  }
}