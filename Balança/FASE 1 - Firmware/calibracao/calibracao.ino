#include <HX711.h>

#define pinDT1  2
#define pinSCK1 3
#define pinDT2  4
#define pinSCK2 5
#define pinDT3  6
#define pinSCK3 7
#define pinDT4  8
#define pinSCK4 9

const float KNOWN_WEIGHT = 92.200;

HX711 scale1;
HX711 scale2;
HX711 scale3;
HX711 scale4;

float medida1 = 0;
float medida2 = 0;
float medida3 = 0;
float medida4 = 0;

float calibration_factor1 = 1;
float calibration_factor2 = 1;
float calibration_factor3 = 1;
float calibration_factor4 = 1;

int currentScale = 1;
bool calibrated = false;

unsigned long previousMillis = 0;
const long interval = 10000;

void setup() {
  Serial.begin(57600);

  scale1.begin(pinDT1, pinSCK1);
  scale2.begin(pinDT2, pinSCK2);
  scale3.begin(pinDT3, pinSCK3);
  scale4.begin(pinDT4, pinSCK4);

  scale1.set_scale();
  scale2.set_scale();
  scale3.set_scale();
  scale4.set_scale();

  delay(2000);

  scale1.tare();
  scale2.tare();
  scale3.tare();
  scale4.tare();

  Serial.println("Balanças Zeradas");
  Serial.println("Para calibrar a balança 1, digite '1'");
  Serial.println("Para calibrar a balança 2, digite '2'");
  Serial.println("Para calibrar a balança 3, digite '3'");
  Serial.println("Para calibrar a balança 4, digite '4'");
  Serial.println("Para inicializar as balanças com os valores de calibração, digite 'i'");
}

void loop() {
  unsigned long currentMillis = millis();

  if (!calibrated) {
    if (Serial.available() > 0) {
      char command = Serial.read();
      if (command == '1' || command == '2' || command == '3' || command == '4') {
        currentScale = command - '0';
        calibrateScale();
      } else if (command == 'i') {
        initializeScales();
      }
    }
  } else {
    readScales();

    if (currentMillis - previousMillis >= interval) {
      previousMillis = currentMillis;
      printAverage();
    }
  }
}

void calibrateScale() {
  HX711* currentScalePtr;
  float* currentCalibrationFactorPtr;

  switch (currentScale) {
    case 1:
      currentScalePtr = &scale1;
      currentCalibrationFactorPtr = &calibration_factor1;
      break;
    case 2:
      currentScalePtr = &scale2;
      currentCalibrationFactorPtr = &calibration_factor2;
      break;
    case 3:
      currentScalePtr = &scale3;
      currentCalibrationFactorPtr = &calibration_factor3;
      break;
    case 4:
      currentScalePtr = &scale4;
      currentCalibrationFactorPtr = &calibration_factor4;
      break;
    default:
      Serial.println("Balança inválida");
      return;
  }

  long start_time = millis();
  long duration = 10000; // 10 segundos
  float sum = 0;
  int count = 0;

  Serial.print("Iniciando calibração da balança ");
  Serial.println(currentScale);

  while (millis() - start_time < duration) {
    sum += currentScalePtr->get_units(1);
    count++;
    delay(100);
  }

  float average = sum / count;

  *currentCalibrationFactorPtr = average / KNOWN_WEIGHT;

  currentScalePtr->set_scale(*currentCalibrationFactorPtr);

  Serial.print("Calibração da balança ");
  Serial.print(currentScale);
  Serial.print(" completa. Fator de calibração: ");
  Serial.println(*currentCalibrationFactorPtr);
}

void initializeScales() {
  scale1.set_scale(calibration_factor1);
  scale2.set_scale(calibration_factor2);
  scale3.set_scale(calibration_factor3);
  scale4.set_scale(calibration_factor4);

  scale1.tare();
  scale2.tare();
  scale3.tare();
  scale4.tare();

  Serial.println("Balanças inicializadas com os valores de calibração");
  
  calibrated = true;
}

void readScales() {
  medida1 = scale1.get_units(5);
  medida2 = scale2.get_units(5);
  medida3 = scale3.get_units(5);
  medida4 = scale4.get_units(5);

  Serial.print("Medida 1: ");
  Serial.println(medida1, 3);

  Serial.print("Medida 2: ");
  Serial.println(medida2, 3);

  Serial.print("Medida 3: ");
  Serial.println(medida3, 3);

  Serial.print("Medida 4: ");
  Serial.println(medida4, 3);
}

void printAverage() {
  Serial.println("Calculando média individual das balanças...");
  
  float average1 = 0;
  float average2 = 0;
  float average3 = 0;
  float average4 = 0;

  for (int i = 0; i < 10; i++) {
    average1 += scale1.get_units(1);
    average2 += scale2.get_units(1);
    average3 += scale3.get_units(1);
    average4 += scale4.get_units(1);
    delay(1000);
  }

  average1 /= 10;
  average2 /= 10;
  average3 /= 10;
  average4 /= 10;

  Serial.print("Valor médio medida 1: ");
  Serial.println(average1, 3);
  
  Serial.print("Valor médio medida 2: ");
  Serial.println(average2, 3);

  Serial.print("Valor médio medida 3: ");
  Serial.println(average3, 3);

  Serial.print("Valor médio medida 4: ");
  Serial.println(average4, 3);
}