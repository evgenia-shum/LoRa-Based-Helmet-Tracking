#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>
#include <Arduino.h>
#include <SPI.h>
#include "STM32LowPower.h"
#include "STM32IntRef.h"
#include "LoRa_STM32.h"
#include <but.h>
#include <LSM6DS3Sensor.h>
#include <Wire.h>

#define SS PA_4
#define RST PB_1
#define DIO0 PB_5
#define ENCRYPT 0x78
#define BAND 868E6
#define TIMEOUT 100  

float latitude = 0.0;
float longitude = 0.0;
float altitude = 0.0;
uint8_t day;
uint8_t month;
uint16_t year;
uint8_t hour;
uint8_t mins;
uint8_t sec;
int32_t accelerometer[3];
int32_t gyroscope[3];

//String length;
String data;
char header;
bool recievedFlag, startParse;
bool gps_flag = true;
bool but_flag = false;
bool receive_flag = false;
bool freefall_flag = false; 
unsigned long parseTime;
String incoming = "";


static const int  RXPin = PA_10, 
                  TXPin = PA_9,
                  Buzzer = PB_12,
                  Vibro = PB_4,
                  LED1 = PC13,
                  But = PA_0;

static const uint32_t GPSBaud = 9600;
volatile int mems_event = 0;

TinyGPSPlus gps;
SoftwareSerial ss(RXPin, TXPin); 
HardwareSerial debug_s(USART2); // PA3  (RX)  PA2  (TX)
TwoWire myWire;
button bt(PA_0);
LSM6DS3Sensor AccGyr(&myWire, LSM6DS3_ACC_GYRO_I2C_ADDRESS_HIGH);


void gps_read(void);
void answer(String incoming);
bool runEvery(unsigned long interval);
void onReceive(int packetSize);
void signal(int delay_on, int delay_off);


void INT1Event_cb()
{
  mems_event = 1;
  //detachInterrupt(PA_1);
}

void gps_flag_func(void){
  gps_flag = true;
  
}

void receive_flag_func(void){
  
  receive_flag = true;
  
}

void but_flag_func(void){
  if (bt.click()) {
    but_flag = true;
    signal(400, 100);
  }  
}

void setup()
{
  pinMode(Buzzer, OUTPUT);
  pinMode(Vibro, OUTPUT);
  pinMode(LED1, OUTPUT);
  pinMode(But, INPUT);
  digitalWrite(LED1, LOW);
  delay(1000);
  digitalWrite(LED1, HIGH);

  ss.begin(GPSBaud);
  debug_s.begin(115200);

  myWire.setSDA(PB_7);
  myWire.setSCL(PB_6); // sda scl
  myWire.begin();
  attachInterrupt(PA_1, INT1Event_cb, RISING);
  AccGyr.begin();
  AccGyr.Enable_X();
  AccGyr.Enable_G();
  AccGyr.Enable_Free_Fall_Detection();

  LoRa.setSignalBandwidth(125e3);
  LoRa.setSpreadingFactor(7);
  LoRa.setTxPower(17);
  LoRa.setSyncWord(ENCRYPT);
  LoRa.setPins(SS, RST, DIO0);
  LoRa.setSPIFrequency(2000000); //max 10mhz
  debug_s.println(F("LoRa Sender"));
  
  #if defined(TIM1)
    TIM_TypeDef *Instance = TIM1;
  #endif
  #if defined(TIM2)
    TIM_TypeDef *Instance2 = TIM2;
  #endif
  #if defined(TIM3)
    TIM_TypeDef *Instance3 = TIM3;
  #endif
  
  HardwareTimer *MyTim = new HardwareTimer(Instance);
  HardwareTimer *MyTim2 = new HardwareTimer(Instance2);
  HardwareTimer *MyTim3 = new HardwareTimer(Instance3);


  MyTim->setOverflow(5000000, MICROSEC_FORMAT);
  MyTim->attachInterrupt(gps_flag_func);
  MyTim->resume();

  MyTim2->setOverflow(500000, MICROSEC_FORMAT);
  MyTim2->attachInterrupt(but_flag_func);
  MyTim2->resume();
  
  MyTim3->setOverflow(100000, MICROSEC_FORMAT);
  MyTim3->attachInterrupt(receive_flag_func);
  MyTim3->resume();

  if (!LoRa.begin(BAND)){
    debug_s.println(F("Starting LoRa failed!"));
    while (1);
  }
}


void loop()
{

      while (ss.available() > 0){
              gps.encode(ss.read());
          }  

      if (gps_flag){
          
        gps_read();
        gps_flag=false;
      }
      AccGyr.Get_X_Axes(accelerometer);
      AccGyr.Get_G_Axes(gyroscope);
      if (receive_flag) onReceive(LoRa.parsePacket());
      if (incoming!="") answer(incoming);     
      if (mems_event){
        mems_event = 0;
        LSM6DS3_Event_Status_t status;
        AccGyr.Get_Event_Status(&status);
        if (status.FreeFallStatus){
            freefall_flag = true;
            // Output data.
            debug_s.println("Free Fall Detected!");
        }
  }


}

void gps_read()
{
 if ((gps.location.isValid()) || (gps.date.isValid()) || (gps.time.isValid())){
    if ((gps.location.isUpdated()) || (gps.date.isUpdated()) || (gps.time.isUpdated())){
        data = "";
        latitude = gps.location.lat();
        longitude = gps.location.lng();
        altitude = gps.altitude.meters();
        day = gps.date.day();
        month  = gps.date.month();
        year = gps.date.year();
        hour  = gps.time.hour();
        mins = gps.time.minute();
        sec  = gps.time.second();
        
        data += (latitude);  
        data += (",");
        data += (longitude);      
        data += (",");
        data += (altitude);      
        data += (",");
        data += (day);
        data += (",");
        data += (month);
        data += (",");
        data += (year);
        data += (",");
        data += (hour);
        data += (",");
        data += (mins);
        data += (",");
        data += (sec);

        LoRa.beginPacket();                   // start packet
        // LoRa.write(data.length()); 
        //LoRa.print(data);
        LoRa.print(latitude, 9);    
        LoRa.print(",");
        LoRa.print(longitude, 9);     
        LoRa.print(",");
        LoRa.print(altitude, 9);      
        LoRa.print(",");
        /*LoRa.print(day);           
        LoRa.print(",");
        LoRa.print(month);         
        LoRa.print(",");
        LoRa.print(year);         
        LoRa.print(",");*/
        LoRa.print(hour);          
        LoRa.print(",");
        LoRa.print(mins);          
        LoRa.print(",");
        LoRa.print(sec);
        LoRa.print(",");
        LoRa.print(accelerometer[0]);           
        LoRa.print(",");
        LoRa.print(accelerometer[1]);         
        LoRa.print(",");
        LoRa.print(accelerometer[2]);          
        LoRa.print(",");
        LoRa.print(gyroscope[0]);          
        LoRa.print(",");
        LoRa.print(gyroscope[1]);          
        LoRa.print(",");
        LoRa.print(gyroscope[2]);
        LoRa.print(",");
        LoRa.print(but_flag);
        LoRa.print(",");
        LoRa.print(freefall_flag);
        LoRa.endPacket();
        
        //debug
        debug_s.print(latitude, 9);    //0
        debug_s.print(",");
        debug_s.print(longitude, 9);     //1
        debug_s.print(",");
        debug_s.print(day);           //2
        debug_s.print("/");
        debug_s.print(month);         //3
        debug_s.print("/");
        debug_s.print(year);          //4
        debug_s.print("  ");
        debug_s.print(hour);          //5
        debug_s.print(":");
        debug_s.print(mins);          //6
        debug_s.print(":");
        debug_s.print(sec);           //7
        debug_s.print("| Acc[mg]: ");
        debug_s.print(accelerometer[0]);
        debug_s.print(" ");
        debug_s.print(accelerometer[1]);
        debug_s.print(" ");
        debug_s.print(accelerometer[2]);
        debug_s.print(" | Gyr[mdps]: ");
        debug_s.print(gyroscope[0]);
        debug_s.print(" ");
        debug_s.print(gyroscope[1]);
        debug_s.print(" ");
        debug_s.print(gyroscope[2]);
        debug_s.print(" /");
        debug_s.print(but_flag);
        debug_s.print(" /");
        debug_s.print(freefall_flag);
        if (but_flag) but_flag = false;
        if (freefall_flag) freefall_flag = false;
    
    
    }
 }
 else{
    debug_s.println(F("INVALID"));
 }

}


void onReceive(int packetSize) {

  
  if (packetSize == 0) return;          // if there's no packet, return

 // byte incomingLength = LoRa.read();    // incoming msg length
  
  incoming="";
  //debug_s.print(F("Received packet: "));
  while (LoRa.available()) {
   //length = LoRa.read();
      
      incoming = (char)LoRa.read();
      debug_s.print(incoming);
  }
/*
  if (incomingLength != incoming.length()) {   // check length for error
    debug_s.println(F("error: message length does not match length"));
    return;                             // skip rest of function
  }*/

}


void answer(String incoming)
{
  char* key = &incoming[0];
  if (isAlpha(key[0]) && !startParse) {     // если префикс БУКВА и парсинг не идёт
      header = key[0];                        // запоминаем префикс
      startParse = true;                        // флаг на парсинг
      parseTime = millis();                     // запоминаем таймер
    }
  //if (debug_s.available() > 0){ //для терминала
   //     key = debug_s.read();
  
  if (startParse) {                           // если парсим
      if (! isDigit(key[0])) {                // если приходит НЕ ЦИФРА
        switch (header){
                    
                    case 'f': 
                          digitalWrite (Buzzer, LOW);
                          digitalWrite (Vibro, LOW);
                          digitalWrite (LED1, HIGH);
                          
                          break;
                    case 'a': 
                              
                              signal(500, 500); //длинный
                              

                            break;
                            
                    case 'b':
                              
                              signal(100, 100); //короткий
                              
                              
                            break;
                    case 'c':
                    
                            //signal(400, 100); //единичный (перенести на кнопку)
                            digitalWrite(LED1,LOW);
                            
                            break;
                    case 'd':
                             //sos
                              signal(70, 700);
                              signal(70, 700);
                              signal(70, 700);
                              signal(300, 700);
                              signal(300, 700);
                              signal(300, 700);
                              
                            break;
        }
        
        recievedFlag = true;                  // данные приняты
        startParse = false;                   // парсинг завершён
        
      } 
    
        // }

  }
  if (startParse && (millis() - parseTime > TIMEOUT)) {
      startParse = false;                   // парсинг завершён по причине таймаута
  }

  
}


void signal(int delay_on, int delay_off)
{
 
    for(int i =0; i<delay_on; i++){
      while ((runEvery(1))==false){
      digitalWrite (Buzzer, HIGH);
      //digitalWrite (Vibro, HIGH);
      digitalWrite (LED1, LOW);
    }
     while ((runEvery(1))==false){
      digitalWrite (Buzzer, LOW);
      //digitalWrite (Vibro, LOW);
      digitalWrite (LED1, HIGH);
      }       
    }

    while ((runEvery(delay_off))==false){
      digitalWrite (Buzzer, LOW);
      //digitalWrite (Vibro, LOW);
      digitalWrite (LED1, HIGH);
    }
}

bool runEvery(unsigned long interval)
{
  static unsigned long previousMillis = 0;
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval)
  {
    previousMillis = currentMillis;
    return true;
  }
  return false;
}


/* MiniPill LoRa v1.x mapping - LoRa module RFM95W and BME280 sensor
  желPA4  // SPI1_NSS   NSS  - RFM95W
  зелPA5  // SPI1_SCK   SCK  - RFM95W - BME280
  краPA6  // SPI1_MISO  MISO - RFM95W - BME280
  синPA7  // SPI1_MOSI  MOSI - RFM95W - BME280

  оранPB10 // USART1_RX  DIO0 - RFM95W
  PB4  //            DIO1 - RFM95W
  PB5  //            DIO2 - RFM95W

  белPB11  // USART1_TX  RST  - RFM95W

  VCC - 3V3
  GND - GND
*/