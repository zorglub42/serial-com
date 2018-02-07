/*--------------------------------------------------------
 # Module Name : Arduino Library
 # Version : 1.0.0
 #
 # Software Name : SerialCom
 # Version : 1.0
 #
 # Copyright (c) 2015 Zorglub42
 # This software is distributed under the Apache 2 license
 # <http://www.apache.org/licenses/LICENSE-2.0.html>
 #
 ##--------------------------------------------------------
 # File Name   : SerialCom.h
 #
 # Created     : 2015-12
 # Authors     : Zorglub42 <contact(at)zorglub42.fr>
 #
 # Description :
 #     simple example to connect to socket server
 ##--------------------------------------------------------
 # History     :
 # 1.0.0 - 2015-12-03 : Release of the file
 #
 */
#include <SerialCom.h>

// Create object to handle connection to socket server
// Can use as well HardwareSerial as SoftwareSerial
SerialCom com(&Serial);


void setup() {
        // start object
        com.begin(9600);
        com.println("Arduino Started");
}

// REQUIRED METHOD: called from SerailCom object
// This method receive command (cmd) from socket server and return resusts to it
void serialComHandler(char *cmd){
        if (strcmp(cmd,"V") == 0) {
                for (int i=0; i<5; i++) {
                        com.println(analogRead(A0+i));
                        //delay(100);
                }
        }
}

void loop() {
        com.handleSerialCom();
}
