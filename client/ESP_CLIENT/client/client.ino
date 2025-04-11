#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <time.h>
#include "data_sender.h"
#include "wifi_login.h"
#include "esp_sleep.h"
#include "driver/rtc_io.h"

#define WAKEUP_PIN_EXT0     GPIO_NUM_32
#define WAKEUP_LEVEL_EXT0   0          
#define WAKEUP_PIN_EXT1     GPIO_NUM_33
#define WAKEUP_BITMASK_EXT1 (1ULL << WAKEUP_PIN_EXT1)
#define AWAKE_TIME_MS       5000

int LED = 27;
int WakeUpReason = -1;
bool connectToEduroam = false;

//standard wifi credentials
const char* ssid = "Net8734";
const char* wifiPassword = "";

//eduroam wifi credentials
char* EAP_ANONYMOUS_IDENTITY = "anonymous@cvut.cz";
char* EAP_IDENTITY = "silpomar@cvut.cz";
char* EAP_PASSWORD = "xxx";
char* EAP_USERNAME = "silpomar@cvut.cz";

//ntp setup
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 3600;
const int   daylightOffset_sec = 3600;

//node settings
const char* serverUrl = "http://88.101.189.39:5000/data";
const char* node_id = "T2_B3_1_0_M_3";
const int stall_id = 1;
const char* nodePassword = "password"; 

bool DEBUG = true;

void setup() {
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);
  Serial.begin(115200);
  delay(100);

  esp_sleep_wakeup_cause_t wakeup_reason = esp_sleep_get_wakeup_cause();
  switch(wakeup_reason) {
    case ESP_SLEEP_WAKEUP_EXT0:
      Serial.println("HALL wake up");
      WakeUpReason = 1;
      break;
    case ESP_SLEEP_WAKEUP_EXT1:
      Serial.println("PIR wake up");
      WakeUpReason = 2;
      break;
    case ESP_SLEEP_WAKEUP_TIMER:
      Serial.println("timer wake up");
      break;
    default:
      Serial.println("other wake up");
      break;
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
  if (WakeUpReason != -1)
  {
    sendData(WakeUpReason, "00:00:00") ;
  }
  digitalWrite(LED, LOW);
  Serial.println("going to sleep");
  Serial.flush();

  //setting wakeups
  esp_sleep_enable_ext0_wakeup(WAKEUP_PIN_EXT0, WAKEUP_LEVEL_EXT0);
  rtc_gpio_pulldown_en(WAKEUP_PIN_EXT0);
  rtc_gpio_pullup_dis(WAKEUP_PIN_EXT0);
  esp_sleep_enable_ext1_wakeup_io(WAKEUP_BITMASK_EXT1, ESP_EXT1_WAKEUP_ANY_HIGH);
  rtc_gpio_pullup_dis(WAKEUP_PIN_EXT1);
  rtc_gpio_pulldown_en(WAKEUP_PIN_EXT1);
  esp_deep_sleep_start();
}
