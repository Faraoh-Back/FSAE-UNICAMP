  /**
 *
 * HX711 library for Arduino - example file
 * https://github.com/bogde/HX711
 *
 * MIT License
 * (c) 2018 Bogdan Necula
 *
**/
#include "HX711.h"


// HX711 circuit wiring
const int LOADCELL_DOUT_PIN1 = 2;
const int LOADCELL_SCK_PIN1 = 3;
const int LOADCELL_DOUT_PIN2 = 4;
const int LOADCELL_SCK_PIN2 = 5;

const int buttonPin = 7;     // the number of the pushbutton pin
//const int ledPin =  13;      // the number of the LED pin

// variables will change:


int buttonState = 0;         // variable for reading the pushbutton status

HX711 scale1;
HX711 scale2;
void setup() {
  
 
  pinMode(buttonPin, INPUT);  // initialize the pushbutton pin as an input
  
  Serial.begin(38400);
  Serial.println("HX711 Demo");

  Serial.println("Initializing the scale");

  // Initialize library with data output pin, clock input pin and gain factor.
  // Channel selection is made by passing the appropriate gain:
  // - With a gain factor of 64 or 128, channel A is selected
  // - With a gain factor of 32, channel B is selected
  // By omitting the gain factor parameter, the library
  // default "128" (Channel A) is used here.
 
   scale1.begin(LOADCELL_DOUT_PIN1, LOADCELL_SCK_PIN1);
   scale2.begin(LOADCELL_DOUT_PIN2, LOADCELL_SCK_PIN2);


  scale1.tare();
  scale2.tare();
  Serial.println("Before setting up the scale:");
  Serial.print("read1: \t\t");
  Serial.println(scale1.read());
  Serial.print("read2: \t\t");
  Serial.println(scale2.read());			// print a raw reading from the ADC

  Serial.print("read average1: \t\t");
  Serial.println(scale1.read_average(20)); 
  Serial.print("read average2: \t\t");
  Serial.println(scale2.read_average(20)); 	// print the average of 20 readings from the ADC

  Serial.print("get value1: \t\t");
  Serial.println(scale1.get_value(5));
  Serial.print("get value2: \t\t");
  Serial.println(scale2.get_value(5));		// print the average of 5 readings from the ADC minus the tare weight (not set yet)
		

  Serial.print("get units1: \t\t");
  Serial.println(scale1.get_units(5), 1);
  Serial.print("get units2: \t\t");
  Serial.println(scale2.get_units(5), 1);	// print the average of 5 readings from the ADC minus tare weight (not set) divided
						// by the SCALE parameter (not set yet)

  scale1.set_scale(42.79);                      // this value is obtained by calibrating the scale with known weights; see the README for details
  scale1.tare();				            // reset the scale to 0
  scale2.set_scale(43.09 );                      // this value is obtained by calibrating the scale with known weights; see the README for details
  scale2.tare();

  


  Serial.println("After setting up the scale:");

  Serial.print("read1: \t\t");
  Serial.println(scale1.read()); 
  Serial.print("read2: \t\t");
  Serial.println(scale2.read());   // print a raw reading from the ADC

  Serial.print("read average1: \t\t");
  Serial.println(scale1.read_average(20)); 
  
  Serial.print("read average: \t\t");
  Serial.println(scale2.read_average(20));   // print the average of 20 readings from the ADC

  Serial.print("get value:1 \t\t");
  Serial.println(scale1.get_value(5));
  
  Serial.print("get value:2 \t\t");
  Serial.println(scale2.get_value(5));		// print the average of 5 readings from the ADC minus the tare weight, set with tare()

  Serial.print("get units:1 \t\t");
  Serial.println(scale1.get_units(5), 1);
  
  Serial.print("get units:2 \t\t");
  Serial.println(scale2.get_units(5), 1);  // print the average of 5 readings from the ADC minus tare weight, divided
						// by the SCALE parameter set with set_scale

  Serial.println("Readings:");
}

void loop() {

  //---------------------------------------------------------------------------------------------------------------------------------------------
  //Se for necessário zerar as células manualmente habilitar as linha sabaixo
  buttonState = digitalRead(buttonPin);// read the state of the pushbutton value

  if (buttonState == LOW) {     
        
  scale1.tare(); 
  scale2.tare(); 
  } 
  //-------------------------------------------------------------------------------------------------------------------------------------------
  Serial.print("<");
  Serial.print("one reading1:\t");
  Serial.print(scale1.get_units(5), 1);
  //Serial.print("\t| average1:\t");
  Serial.print(";");
  
  //Serial.print("  ||  one reading2:\t");
  Serial.print(scale2.get_units(5), 1);
  //Serial.print("\t| average2:\t");
  Serial.println(">");
  scale1.power_down();
  scale2.power_down();		          
  delay(1000);
  scale1.power_up();
  scale2.power_up();

}
