// for windows apparently drivers are necessary: http://www.wch.cn/download/CH341SER_EXE.html
void setup() {
   Serial.begin(9600);

}

void loop() {
  // put your main code here, to run repeatedly:
   int sensorValue_a1 = analogRead(A1);
   int sensorValue_a2 = analogRead(A2);
   int level_a1 = 0;
   int level_a2 = 0;
   // Convert the analog reading (which goes from 0 - 1023) to a voltage (0 - 5V):
   double voltage_a1 = sensorValue_a1 * (5.0 / 1023.0);
   double voltage_a2 = sensorValue_a2 * (5.0 / 1023.0);
   char data[20] = "test2";
   // print out the value you read:
   if (voltage_a1>2.0){
    level_a1 = 1;
   }else{
    level_a1 = 0;
   }
   if (voltage_a2 > 2.0){
    level_a2 = 1;
   } else {
    level_a2 = 0;
   }
   sprintf(data,"hutch %d remote %d", level_a1, level_a2);
   Serial.println(data);
   delay(500);
}
