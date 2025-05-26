#ifndef WIFI_LOGIN_H
#define WIFI_LOGIN_H
#ifdef __cplusplus
extern "C" {
#endif

// Funkce pro sestavení a odeslání dat
void logInWifi(const char* ssid, const char* Password);
void logInEduroam(char* EAP_IDENTITY, char* EAP_USERNAME, char* EAP_PASSWORD);

#ifdef __cplusplus
}
#endif

#endif // DATA_SENDER_H