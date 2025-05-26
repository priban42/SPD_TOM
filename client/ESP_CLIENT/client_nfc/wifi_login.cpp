#include <WiFi.h>
#include "wifi_login.h"
#include "esp_eap_client.h"

extern bool DEBUG;

void logInWifi(const char* ssid, const char* Password) {
  Serial.print("connection to standard wifi SSID: ");
  Serial.println(ssid);
  WiFi.begin(ssid, Password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("Connected. Local address: ");
  Serial.println(WiFi.localIP());
}


void logInEduroam(char* EAP_IDENTITY, char* EAP_USERNAME, char* EAP_PASSWORD) {
  Serial.println("connecting to eduroam");
  WiFi.disconnect(true);
  WiFi.begin("eduroam", WPA2_AUTH_PEAP, EAP_IDENTITY, EAP_USERNAME, EAP_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(F("."));
  }
  if (DEBUG)
  {
      Serial.println("");
      Serial.println(F("WiFi is connected!"));
      Serial.println(F("IP address set: "));
      Serial.println(WiFi.localIP());
    
    }
}