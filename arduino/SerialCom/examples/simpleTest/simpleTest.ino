#include <SoftwareSerial.h>
#include "SerialCom.h"


SerialCom com(&Serial);
void setup() {
  // put your setup code here, to run once:
  com.begin(9600);
  com.println("Arduino Started");
}


void serialComHandler(char *cmd){
  if (strcmp(cmd,"V") == 0){
    for (int i=0;i<5;i++){
      com.println(analogRead(A0+i));
      //delay(100);
    }
  }
}

void loop() {
  com.handleSerialCom();
}
