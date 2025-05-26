#ifndef DATA_SENDER_H
#define DATA_SENDER_H

#ifdef __cplusplus
extern "C" {
#endif

// Deklarace globálních proměnných
extern const int stall_id;

// Funkce pro sestavení a odeslání dat
void sendData(int event, char* tag_id, int action);

#ifdef __cplusplus
}
#endif

#endif // DATA_SENDER_H