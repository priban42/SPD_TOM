#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <time.h>
#include "data_sender.h"
#include "wifi_login.h"
#include "esp_sleep.h"
#include "driver/rtc_io.h"
#include <Wire.h>
#include <Adafruit_PN532.h>
//#include <PN532_I2C.h>
//#include <PN532.h>
//#include <NfcAdapter.h>

//NFC setup
//PN532_I2C pn532_i2c(Wire);
//NfcAdapter nfc = NfcAdapter(pn532_i2c);
#define PN532_Serial Serial2
Adafruit_PN532 nfc(PN532_Serial);

const int ledR = 32;
const int ledG = 33;
const int btnR = 25;
const int btnG = 26;

bool connectToEduroam = false;

//standard wifi credentials
const char* ssid = "Net8734";
const char* wifiPassword = ".,VEma71";

//eduroam wifi credentials
char* EAP_ANONYMOUS_IDENTITY = "anonymous@cvut.cz";
char* EAP_IDENTITY = "silpomar@cvut.cz";
char* EAP_PASSWORD = "aDZT33F4nUpDTUw";
char* EAP_USERNAME = "silpomar@cvut.cz";

//ntp setup
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 3600;
const int   daylightOffset_sec = 3600;

//node settings
const char* serverUrl = "http://88.101.189.39:5000/data";
const char* node_id = "T2_B2_1_0_F_3";
const int stall_id = -1;
const char* nodePassword = "password"; 

bool DEBUG = true;
String UID = "";

void setup() {
  ///pinMode(ledR, OUTPUT);
  ///pinMode(ledG, OUTPUT);
  ///pinMode(btnR, INPUT_PULLUP);
  ///pinMode(btnG, INPUT_PULLUP);
  ///digitalWrite(ledR, LOW);
  ///digitalWrite(ledG, LOW);
  

  Serial.begin(115200);
  delay(100);
  PN532_Serial.begin(115200, SERIAL_8N1, 21, 22); // RX=16, TX=17
  
  nfc.begin();
    uint32_t versiondata = nfc.getFirmwareVersion();
  if (!versiondata) {
    Serial.println("Nepodařilo se najít PN532.");
    while (1); // Zastav program
  }
  //connect to wifi
  if (connectToEduroam)
    {
      logInEduroam(EAP_IDENTITY, EAP_USERNAME, EAP_PASSWORD);
    }
  else
  {
    logInWifi(ssid, wifiPassword);
  }


  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
}


void loop() {
  if (digitalRead(btnR)){
    digitalWrite(ledR, HIGH);
  }
  else
  {
    digitalWrite(ledR, LOW);
  }
  if (digitalRead(btnG)){
    digitalWrite(ledG,HIGH);
  }
  else
  {
    digitalWrite(ledG, LOW);
  }
  //////if(nfc.tagPresent()){
  //////NfcTag tag = nfc.read();
  //////UID = tag.getUidString();
  //////Serial.print("UID: ");
  //////Serial.println(UID);
  //////}
  ////////digitalWrite(LED, HIGH);
  //////int length = UID.length();
  //////char* buffer = new char[length + 1];
  //////UID.toCharArray(buffer, length + 1);
  //////sendData(3, buffer) ;
  //////delete[] buffer;
  //////delay(1000);
  //digitalWrite(LED, LOW);
  ///////}
}
