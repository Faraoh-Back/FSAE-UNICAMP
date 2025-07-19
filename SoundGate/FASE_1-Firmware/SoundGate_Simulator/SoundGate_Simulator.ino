/*
 * SoundGate - FIRMWARE SIMULADOR
 * * Descrição:
 * Este firmware NÃO utiliza o sensor ultrassônico. Ele foi criado para
 * testar a cadeia de software (Coletor Serial, Processador e Dashboard)
 * simulando a passagem de um carro em intervalos aleatórios de 4 a 5 segundos.
 * * A saída serial é IDÊNTICA à do firmware real, garantindo compatibilidade.
 */

// --- Variáveis de Simulação ---
unsigned long proximaPassagem = 0; // Armazena o tempo em milissegundos da próxima "passagem" do carro.
int voltas = 0;

// --- Variáveis de Tempo (iguais ao firmware real) ---
unsigned long tempoInicial = 0;
unsigned long tempoDaUltimaVolta = 0;


void setup() {
  Serial.begin(9600);
  
  // Mensagens iniciais
  Serial.println("FSAE - SoundGate");
  Serial.println(">>> MODO SIMULADOR ATIVO <<<"); // Avisa que é o simulador
  Serial.println("Aguardando passagem do carro...");
  
  // Cabeçalho para CSV (idêntico ao original)
  Serial.println("Volta,Distancia,Tempo de Volta,Tempo Total");
  
  // Agenda a primeira passagem para 5 segundos após o boot
  proximaPassagem = millis() + 5000; 
}

void loop() {
  // Verifica se já chegou a hora de simular a próxima passagem
  if (millis() >= proximaPassagem) {
    
    unsigned long tempoAtual = millis();
    
    // Se for a primeira volta, inicializa os contadores de tempo
    if (voltas == 0) {
      tempoInicial = tempoAtual;
      tempoDaUltimaVolta = tempoAtual;
    }
    
    
    // --- Geração de Dados Falsos ---
    // Gera uma distância aleatória entre 45.00 e 65.00 cm
    float distanciaFalsa = random(4500, 6501) / 100.0;
    
    // Calcula os tempos
    unsigned long tempoDeVoltaMs = tempoAtual - tempoDaUltimaVolta;
    unsigned long tempoTotalMs = tempoAtual - tempoInicial;

    // --- Impressão dos Dados no formato CSV (bloco de código idêntico ao firmware real) ---
    
    // Volta
    Serial.print(voltas);
    Serial.print(",");
    
    // Distância (agora com o valor falso)
    Serial.print(distanciaFalsa);
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
    
    // --- Fim do Bloco de Impressão ---
    
    // Atualiza o marcador de tempo para a próxima volta
    tempoDaUltimaVolta = tempoAtual;
    
    // Agenda a próxima passagem para daqui a 4 ou 5 segundos
    proximaPassagem = millis() + random(4000, 5001); // random(min, max) -> max é exclusivo
    
    // Incrementa o número de voltas
    voltas++;

  }
}