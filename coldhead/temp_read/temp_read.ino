#include <OneWire.h>
#include <DallasTemperature.h>
 
// Data wire is plugged into pin 2 on the Arduino
#define hotbodybus 2
#define coldbodybus 4

int analogPin = 3;
int hbval = 0;
double temp = 0.0;
double volt = 0.0;
String S = "";

// Setup a oneWire instance to communicate with any OneWire devices 
// (not just Maxim/Dallas temperature ICs)
OneWire hotbody(hotbodybus);
OneWire coldbody(coldbodybus);
 
// Pass our oneWire reference to Dallas Temperature.
DallasTemperature hotsensors(&hotbody);
DallasTemperature coldsensors(&coldbody);
 
void setup(void)
{
  // start serial port
  Serial.begin(9600);
  Serial.println("Arduino - hot and cold blackbody temperatures");

  // Start up the library
  hotsensors.begin();
  coldsensors.begin();
}

//https://computers.tutsplus.com/tutorials/how-to-read-temperatures-with-arduino--mac-53714
double Thermister(int RawADC) {  //Function to perform the fancy math of the Steinhart-Hart equation
 double Temp;
 Temp = log(((10240000/RawADC) - 10000));
 Temp = 1 / (0.001129148 + (0.000234125 + (0.0000000876741 * Temp * Temp ))* Temp );
 Temp = Temp - 273.15;              // Convert Kelvin to Celsius
 return Temp;
}

double Voltage(int val) {
  double volt;
  volt = val * (5.0 / 1023.0);
  return volt;
}
 
void loop(void)
{
  // call sensors.requestTemperatures() to issue a global temperature
  // request to all devices on the bus
  //Serial.print(" Requesting temperatures...");
  hotsensors.requestTemperatures(); // Send the command to get temperatures
  coldsensors.requestTemperatures(); // Send the command to get temperatures
  //Serial.println("DONE");
  hbval = analogRead(analogPin);
  temp = Thermister(hbval);
  volt = Voltage(hbval);
  //
  //Serial.print("H ");
  S = String(hotsensors.getTempCByIndex(0));
  S = String(S + String(" "));
  S = String(S + String(hotsensors.getTempCByIndex(1)));
  S = String(S + String(" "));
  S = String(S + String(hotsensors.getTempCByIndex(2)));
  S = String(S + String(" "));
  S = String(S + String(hotsensors.getTempCByIndex(3)));
  //Serial.print(hotsensors.getTempCByIndex(0));
  //Serial.print(" ");
  //Serial.print(hotsensors.getTempCByIndex(1));
  //Serial.print(" ");
  //Serial.print(hotsensors.getTempCByIndex(2));
  //Serial.print(" ");
  //Serial.print(hotsensors.getTempCByIndex(3));
  //Serial.print(" ");
  //Serial.print(hbval);
  S = String(S + String(" "));
  S = String(S + String(volt));
  
  //Serial.print(volt);
  
  //Serial.print(temp);
  //
  //Serial.print("\n"); // Why "byIndex"? 
  //Serial.print("C ");
  S = String(S + String(" "));
  S = String(S + String(coldsensors.getTempCByIndex(0)));
  S = String(S + String(" "));
  S = String(S + String(coldsensors.getTempCByIndex(1)));
  S = String(S + String(" "));
  S = String(S + String(coldsensors.getTempCByIndex(2)));
  S = String(S + String(" "));
  S = String(S + String(coldsensors.getTempCByIndex(3)));
  
  //Serial.print(" ");
  //Serial.print(coldsensors.getTempCByIndex(0));
  //Serial.print(" ");
  //Serial.print(coldsensors.getTempCByIndex(1));
  //Serial.print(" ");
  //Serial.print(coldsensors.getTempCByIndex(2));
  //Serial.print(" ");
  //Serial.print(coldsensors.getTempCByIndex(3));
  //Serial.print("\n"); // Why "byIndex"? 
     // You can have more than one IC on the same bus. 
    // 0 refers to the first IC on the wire
   Serial.println(S);
    delay(1000);
}
