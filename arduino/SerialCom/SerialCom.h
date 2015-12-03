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
 #     Helper class defintion
 #--------------------------------------------------------
 # History     :
 # 1.0.0 - 2015-12-03 : Release of the file
 #
*/
#ifndef __SERIALCOM_CLASS__
#define __SERIALCOM_CLASS__


#include <Arduino.h>
#if (ARDUINO >= 100)
  #include <SoftwareSerial.h>
#else
  #include <NewSoftSerial.h>
#endif

class SerialCom : public Print{
  public:  
    #if ARDUINO >= 100
      SerialCom(SoftwareSerial *);
    #else
      SerialCom(NewSoftSerial *);
    #endif
      SerialCom(HardwareSerial *);
      void begin(uint16_t baud);
      void handleSerialCom();
      virtual size_t write(uint8_t);
      
      
   private:
      #if ARDUINO >= 100
        SoftwareSerial *sws;
      #else
        NewSoftSerial *sws;
      #endif
      uint8_t isHW;
      HardwareSerial *hws;
      Stream *mySerial;
   
};

void serialComHandler(char* command);

#endif
