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
  
  // Mensagens iniciais de balanças zeradas
  Serial.println("<BALANCA FL/1 zerada>");
  Serial.println("<BALANCA FR/2 zerada>");
  Serial.println("<BALANCA RL/3 zerada>");
  Serial.println("<BALANCA RR/4 zerada>");
  
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
  
  // Leituras normais
  Serial.print("<LEITURA; ");
  for (int i = 0; i < NUM_BALANCAS; i++) {
    Serial.print(valores[i], 3);
    if (i < NUM_BALANCAS-1) Serial.print(";");
  }
  Serial.println(">");
  
  // Médias a cada 10 segundos
  if (tempoAtual - tempoInicial >= 10000) {
    Serial.print("<MEDIA; ");
    for (int i = 0; i < NUM_BALANCAS; i++) {
      // Calcula média com pequena variação
      float media = valores[i] + random(-5, 5)/10.0;
      Serial.print(media, 3);
      if (i < NUM_BALANCAS-1) Serial.print(";");
    }
    Serial.println(">");
    
    tempoInicial = millis();
    
    // Muda as tendências periodicamente
    for (int i = 0; i < NUM_BALANCAS; i++) {
      tendencias[i] = random(-10, 10)/10.0;
    }
  }
  
  delay(1000); // Intervalo entre leituras
}