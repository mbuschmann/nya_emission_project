// for windows apparently drivers are necessary: http://www.wch.cn/download/CH341SER_EXE.html
void setup() {
   Serial.begin(9600);

}

void loop() {
  // put your main code here, to run repeatedly:
   int sensorValue = analogRead(A1);
   // Convert the analog reading (which goes from 0 - 1023) to a voltage (0 - 5V):
   double voltage = sensorValue * (5.0 / 1023.0);
   // print out the value you read:
   if (voltage>2.0){
    Serial.print(voltage);
    Serial.println(" open");
    }
   else {
    Serial.print(voltage);
    Serial.println(" closed");
   }
   delay(500);
}
