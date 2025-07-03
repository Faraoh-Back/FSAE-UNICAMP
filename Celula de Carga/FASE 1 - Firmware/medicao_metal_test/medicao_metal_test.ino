#include <Arduino.h>

// Definição do número de balanças
#define NUM_BALANCAS 4

// Variáveis para acompanhar o tempo
unsigned long tempoInicial = 0;
unsigned long tempoAtual = 0;

// Valores iniciais para simulação
float valores[NUM_BALANCAS] = {100.0, 100.0, 100.0, 100.0};
float tendencias[NUM_BALANCAS] = {0.5, -0.3, 0.2, -0.4};
float variacoes[NUM_BALANCAS] = {2.0, 3.0, 1.5, 2.5};

void setup() {
  Serial.begin(57600);
  randomSeed(analogRead(0)); // Semente aleatória baseada em pin flutuante
  
  tempoInicial = millis();
}

void loop() {
  tempoAtual = millis();
  
  // Simulação de mudanças nos valores
  for (int i = 0; i < NUM_BALANCAS; i++) {
    // Aplica tendência + variação aleatória
    float variacao = random(-100, 100) / 100.0 * variacoes[i];
    valores[i] += tendencias[i] + variacao;
    
    // Mantém valores em faixa razoável
    if (valores[i] < 80) valores[i] = 80;
    if (valores[i] > 120) valores[i] = 120;
  }
  
  // Calcula dado1 (média das duas primeiras balanças) e dado2 (média das duas últimas)
  float dado1 = (valores[0] + valores[1]) / 2.0;
  float dado2 = (valores[2] + valores[3]) / 2.0;
  
  // Escreve no formato solicitado
  Serial.print("<");
  Serial.print(dado1, 3);
  Serial.print(";");
  Serial.print(dado2, 3);
  Serial.println(">");
  
  // Médias a cada 10 segundos (opcional - mantido do código original)
  if (tempoAtual - tempoInicial >= 10000) {
    tempoInicial = millis();
    
    // Muda as tendências periodicamente
    for (int i = 0; i < NUM_BALANCAS; i++) {
      tendencias[i] = random(-10, 10)/10.0;
    }
  }
  
  delay(1000); // Intervalo entre leituras
}