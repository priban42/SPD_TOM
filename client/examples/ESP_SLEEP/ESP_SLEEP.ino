#include "esp_sleep.h"
#include "driver/rtc_io.h"

#define WAKEUP_PIN_EXT0     GPIO_NUM_32
#define WAKEUP_LEVEL_EXT0   0          
#define WAKEUP_PIN_EXT1     GPIO_NUM_33
#define WAKEUP_BITMASK_EXT1 (1ULL << WAKEUP_PIN_EXT1)
#define AWAKE_TIME_MS       5000   

void setup() {
  Serial.begin(115200);
  delay(1000); // počkáme na otevření Serial Monitor

  // Vypsání důvodu probuzení
  esp_sleep_wakeup_cause_t wakeup_reason = esp_sleep_get_wakeup_cause();
  Serial.print("Důvod probuzení: ");
  switch(wakeup_reason) {
    case ESP_SLEEP_WAKEUP_EXT0:
      Serial.println("HALL wake up");
      WakeUpReason = 1;
      break;
    case ESP_SLEEP_WAKEUP_EXT1:
      Serial.println("PIR wake up");
      break;
    case ESP_SLEEP_WAKEUP_TIMER:
      Serial.println("Probuzen časovačem");
      break;
    default:
      Serial.println("Power on reset nebo jiný důvod");
      break;
  }

  // Zůstaneme aktivní 5 sekund
  Serial.println("ESP32 je vzhůru 5 sekund.");
  delay(AWAKE_TIME_MS);

  // Nastavení probuzení ext0 na GPIO32 – probudí se, když je na pinu LOW
  esp_sleep_enable_ext0_wakeup(WAKEUP_PIN_EXT0, WAKEUP_LEVEL_EXT0);
  // Pro stabilitu nastavíme vnitřní pull-down pro GPIO32 (a deaktivujeme pull-up)
  rtc_gpio_pulldown_en(WAKEUP_PIN_EXT0);
  rtc_gpio_pullup_dis(WAKEUP_PIN_EXT0);

  // Nastavení probuzení ext1 na GPIO33 – probudí se, když je na pinu HIGH
  esp_sleep_enable_ext1_wakeup_io(WAKEUP_BITMASK_EXT1, ESP_EXT1_WAKEUP_ANY_HIGH);
  // Pro ext1 doporučujeme aktivovat vnitřní pull-up, aby byl pin při neaktivním stavu na HIGH
  rtc_gpio_pullup_en(WAKEUP_PIN_EXT1);
  rtc_gpio_pulldown_dis(WAKEUP_PIN_EXT1);

  Serial.println("Jdu do deep sleep. Probuzení: GPIO32 LOW nebo GPIO33 HIGH");
  Serial.flush();
  esp_deep_sleep_start();
}

void loop() {
  // Tento kód se nikdy nevyvolá, protože ESP32 jde do deep sleep.
}
