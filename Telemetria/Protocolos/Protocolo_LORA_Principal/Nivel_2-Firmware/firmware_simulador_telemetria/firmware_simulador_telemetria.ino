// --- CONSTANTES ---
#define SERIAL_BAUD 115200       // Taxa de comunicação (deve ser a mesma do Python)
const int NUM_SENSORES = 17;     // Quantidade total de sensores na string

// Variável para gerar dados dinâmicos (simulando aceleração/desaceleração)
float angulo_simulacao = 0.0;

void setup() {
  Serial.begin(SERIAL_BAUD);
  while (!Serial) {
    ; // Aguarda a porta serial iniciar
  }
  // Inicializa o gerador de números aleatórios
  randomSeed(analogRead(0));
  
  Serial.println("Simulador de Telemetria Pronto. Aguardando requisição do PC...");
}

void loop() {
  // O Arduino fica ocioso até receber qualquer dado do PC
  if (Serial.available() > 0) {
    // Lê e descarta os dados recebidos. Só nos importa o fato de que algo chegou.
    while(Serial.available() > 0) {
      Serial.read();
    }
    
    // Ao receber a requisição, gera e envia uma nova linha de dados de telemetria
    enviarDadosTelemetria();
  }
}

void enviarDadosTelemetria() {
  // Inicia a string de dados
  Serial.print("<");

  // Loop para gerar e imprimir o dado de cada um dos 17 sensores
  for (int i = 0; i < NUM_SENSORES; i++) {
    float valor_sensor;

    // Gera dados mais realistas para alguns sensores e aleatórios para outros
    switch (i) {
      case 0: // RPM
        // Gera uma onda senoidal para simular aceleração e desaceleração
        valor_sensor = 3500 + 2500 * sin(angulo_simulacao);
        break;
      case 1: // MAP
        valor_sensor = 0.5 + 0.5 * sin(angulo_simulacao);
        break;
      case 2: // Engine Temp
        valor_sensor = 95.0 + random(-20, 20) / 10.0; // Variação pequena em torno de 95°C
        break;
      case 9: // TPS
        valor_sensor = 50.0 + 50.0 * sin(angulo_simulacao); // Acompanha o RPM
        break;
      case 14: // Gear Position
        valor_sensor = random(1, 6); // Marcha de 1 a 5
        break;
      default: // Outros sensores
        // Gera um número aleatório com casas decimais
        valor_sensor = random(0, 5000) / 100.0;
        break;
    }
    
    Serial.print(valor_sensor, 2); // Imprime o valor com 2 casas decimais

    // Adiciona o separador ';' se não for o último sensor
    if (i < NUM_SENSORES - 1) {
      Serial.print(";");
    }
  }

  // Fecha a string e envia um caractere de nova linha
  Serial.println(">");

  // Atualiza o ângulo para a próxima iteração, criando a dinâmica dos dados
  angulo_simulacao += 0.2; 
}