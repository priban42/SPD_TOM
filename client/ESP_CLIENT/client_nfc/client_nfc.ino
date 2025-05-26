#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <time.h>
#include "data_sender.h"
#include "wifi_login.h"
#include "esp_sleep.h"
#include "driver/rtc_io.h"
#include <Wire.h>
#include <PN532_I2C.h>
#include <PN532.h>
#include <NfcAdapter.h>

//NFC setup
//PN532_I2C pn532_i2c(Wire);
//NfcAdapter nfc = NfcAdapter(pn532_i2c);

#define I2C_SDA 21
#define I2C_SCL 22
#define PN532_RESET_PIN  27 
TwoWire I2CBus = TwoWire(0);
PN532_I2C pn532_i2c(I2CBus);
NfcAdapter nfc = NfcAdapter(pn532_i2c);

const int ledR = 32;
const int ledG = 33;
const int btnR = 25;
const int btnG = 26;

bool connectToEduroam = false;

//standard wifi credentials
const char* ssid = "xxx";
const char* wifiPassword = "yyy";

//eduroam wifi credentials
char* EAP_ANONYMOUS_IDENTITY = "anonymous@cvut.cz";
char* EAP_IDENTITY = "xxx@cvut.cz";
char* EAP_PASSWORD = "xxx";
char* EAP_USERNAME = "xxx@cvut.cz";

//ntp setup
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 3600;
const int   daylightOffset_sec = 3600;

//node settings
const char* serverUrl = "http://0.1.2.3:5000/data";
const char* node_id = "T2_B2_1_0_F_3";
const int stall_id = -1;
const char* nodePassword = "password"; 

bool DEBUG = true;
String UID = "";

void setup() {
  pinMode(PN532_RESET_PIN, OUTPUT);
  pinMode(ledR, OUTPUT);
  pinMode(ledG, OUTPUT);
  pinMode(btnR, INPUT_PULLUP);
  pinMode(btnG, INPUT_PULLUP);
  digitalWrite(ledR, LOW);
  digitalWrite(ledG, LOW);
  Serial.begin(115200);

  // reset pn532
  digitalWrite(PN532_RESET_PIN, LOW);
  delay(100);
  digitalWrite(PN532_RESET_PIN, HIGH);
  delay(100);
  I2CBus.end(); 
  delay(100);
  I2CBus.begin(I2C_SDA, I2C_SCL, 400000); 
  nfc.begin();

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
  if (!digitalRead(btnR)){
    digitalWrite(ledR, HIGH);
    Serial.println("STOP button pressed");
    if(readRFID(0)){
    for(int i = 0; i < 10; i++){
      digitalWrite(ledR, LOW);
      delay(100);
      digitalWrite(ledR, HIGH);
      delay(100);
    }
    digitalWrite(ledR, LOW);
    }
    else{
      error();
    }
  }
  if (!digitalRead(btnG)){
    digitalWrite(ledG,HIGH);
    Serial.println("START button pressed");
    if(readRFID(1)){
    for(int i = 0; i < 10; i++){
      digitalWrite(ledG, LOW);
      delay(100);
      digitalWrite(ledG, HIGH);
      delay(100);
    }
    digitalWrite(ledG, LOW);
    }
    else{
      error();
    }
  }
}


bool readRFID(int action)
{
  if(nfc.tagPresent()){
  NfcTag tag = nfc.read();
  UID = tag.getUidString();
  Serial.print("UID: ");
  Serial.println(UID);
  int length = UID.length();
  char* buffer = new char[length + 1];
  UID.toCharArray(buffer, length + 1);
  sendData(3, buffer,action) ;
  delete[] buffer;
  return true;
  }
  return false;
}

void error()
{
  Serial.println("no card detected");
  for(int i = 0; i < 10; i++){
      digitalWrite(ledG, HIGH);
      delay(100);
      digitalWrite(ledG, LOW);
      digitalWrite(ledR, HIGH);
      delay(100);
      digitalWrite(ledR, LOW);
    }
    digitalWrite(ledR, LOW);
    digitalWrite(ledG, LOW);
}