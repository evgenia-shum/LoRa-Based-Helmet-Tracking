#include <Arduino.h>
#include <SoftwareSerial.h>
#include <SPI.h>
#include "TinyGPSPlus.h"
#include "LoRa_STM32.h"
#include <stdio.h>

#define SS PA_4
#define RST PB_5
#define DIO0 PB_13
#define ENCRYPT 0x78
#define BAND 868E6
#define TIMEOUT 100 

bool recievedFlag, startParse;
unsigned long parseTime;


HardwareSerial Serial22(PA_3, PA_2);   // HardWareSerial Serial2 (PA3, PA2);

void sendMessage(String outgoing) ;
void onReceive(int packetSize);
bool runEvery(unsigned long interval);
void receive(void);
long lastSendTime = 0;        // last send time
int interval = 2000;          // interval between sends

 
void setup() {
  Serial22.begin(115200);
  Serial22.setTimeout(100);
  LoRa.setSPIFrequency(8000000); //max 10mhz
  LoRa.setTxPower(17);
  LoRa.setSyncWord(ENCRYPT);
  LoRa.setPins(SS, RST, DIO0);
 
  if (!LoRa.begin(BAND)) 
  {
    Serial22.println(F("Starting LoRa failed!"));
    while (1);
  }
  Serial22.println(F("Hi!"));
}
 
void loop() {

  
      onReceive(LoRa.parsePacket());
      receive();

}

void sendMessage(String outgoing) {
  LoRa.beginPacket();                   // start packet
  LoRa.write(outgoing.length());        // add payload length
  LoRa.print(outgoing);   
  LoRa.endPacket();                     // finish packet and send it
  //Serial22.print(F("done"));
  //Serial22.println(outgoing);
  //Serial22.println(outgoing.length());
}

void onReceive(int packetSize) {
  if (packetSize == 0) return;          // if there's no packet, return

  while (LoRa.available()) {
    Serial22.print((char)LoRa.read());
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

void receive() // принять из команду приложения
{
  
  while (Serial22.available() > 0){
      char array_key [2];
      int amount = Serial22.readBytesUntil(';', array_key, 2);
      array_key[amount] = NULL;
      String out = array_key;
      sendMessage(out);                   
      //Serial22.println(out);    // вывести
      } 
 
}

/* MiniPill LoRa v1.x mapping - LoRa module RFM95W and BME280 sensor
  PA4  // SPI1_NSS   NSS  - RFM95W
  PA5  // SPI1_SCK   SCK  - RFM95W - BME280
  PA6  // SPI1_MISO  MISO - RFM95W - BME280
  PA7  // SPI1_MOSI  MOSI - RFM95W - BME280

  PB10 // USART1_RX  DIO0 - RFM95W
  PB4  //            DIO1 - RFM95W
  PB5  //            DIO2 - RFM95W

  PB15  // USART1_TX  RST  - RFM95W

  VCC - 3V3
  GND - GND
*/
