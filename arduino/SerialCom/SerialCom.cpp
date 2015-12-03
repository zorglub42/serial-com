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
 #--------------------------------------------------------
 # File Name   : SerialCom.h
 #
 # Created     : 2015-12
 # Authors     : Zorglub42 <contact(at)zorglub42.fr>
 #
 # Description :
 #     Helper class implementation
 #--------------------------------------------------------
 # History     :
 # 1.0.0 - 2015-12-03 : Release of the file
 #
*/
#include "SerialCom.h"

#if ARDUINO >= 100
  SerialCom::SerialCom(SoftwareSerial *sws){
    this->isHW=0;
    this->sws=sws;
    this->mySerial=sws;
  }
#else
  SerialCom::SerialCom(NewSoftSerial *sws){
    this->isHW=0;
    this->sws=sws;
    this->mySerial=sws;
  }
#endif
  SerialCom::SerialCom(HardwareSerial *hws){
    this->isHW=1;
    this->hws=hws;
    this->mySerial=hws;
  }



void SerialCom::begin(uint16_t baud){
  if (this->isHW){
    this->hws->begin(baud);
  }else{
    this->sws->begin(baud);
  }
}



void SerialCom::handleSerialCom(){
  if (this->mySerial->available()){
    char cmd[10];
    int i=0;
    char c=0;
    do{
      if (this->mySerial->available()){
        c=this->mySerial->read();
        cmd[i++]=c;
        cmd[i]=0;
      }
      
    }while (c != '\n');
    cmd[i-1]=0;
    mySerial->println(F("***START***"));
    serialComHandler(cmd);
    mySerial->println(F("***DONE***"));
  }
}  


size_t SerialCom::write(uint8_t b){
  this->mySerial->write(b);
}
