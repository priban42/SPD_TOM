#include <Arduino.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <time.h>
#include "data_sender.h"

extern const char* node_id;
extern const char* nodePassword;
extern const char* serverUrl;
extern const int stall_id;
extern bool DEBUG;


void sendData(int event, char* tag_id, int action) {
  struct tm timestamp;
  if (!getLocalTime(&timestamp)) {
    Serial.println("error getting time from NTP");
    return;
  }
  
  if (DEBUG) {
    Serial.println("time now:");
    Serial.printf("%04d-%02d-%02d %02d:%02d:%02d\n",
                  timestamp.tm_year + 1900, timestamp.tm_mon + 1, timestamp.tm_mday,
                  timestamp.tm_hour, timestamp.tm_min, timestamp.tm_sec);
  }
  
  //compose JSON
  StaticJsonDocument<256> jsonDoc;
  jsonDoc["node_id"] = node_id;
  jsonDoc["password"] = nodePassword;
  jsonDoc["elapsed_time"] = 5;
  
  JsonArray timestamps = jsonDoc.createNestedArray("timestamps");
  timestamps.add(0);
  
  JsonArray event_types = jsonDoc.createNestedArray("event_types");
  event_types.add(event);
  
  JsonArray tag_ids = jsonDoc.createNestedArray("tag_ids");
  tag_ids.add(tag_id);
  
  JsonArray stall_ids = jsonDoc.createNestedArray("stall_ids");
  stall_ids.add(action);
  
  String requestBody;
  serializeJson(jsonDoc, requestBody);
  
  Serial.println("JSON payload:");
  Serial.println(requestBody);
  
  //send HTTP request
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");
  
  int httpResponseCode = http.POST(requestBody);
  
  if (httpResponseCode > 0) {
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    String response = http.getString();
    Serial.println("server response:");
    Serial.println(response);
  } else {
    Serial.print("error sending request: ");
    Serial.println(httpResponseCode);
  }
  http.end();
}