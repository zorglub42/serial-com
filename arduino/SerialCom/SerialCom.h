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
