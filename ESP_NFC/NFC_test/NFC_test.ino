#include <Wire.h>
#include <PN532_I2C.h>
#include <PN532.h>
#include <NfcAdapter.h>
PN532_I2C pn532_i2c(Wire);
NfcAdapter nfc = NfcAdapter(pn532_i2c);
String tagId = "None";
byte nuidPICC[4];
 
void setup(void) 
{
 Serial.begin(115200);
 Serial.println("System initialized");
 nfc.begin();
 pinMode(27, OUTPUT);
}
 
void loop() 
{
 readNFC();
}
 
void readNFC() 
{
 if (nfc.tagPresent())
 {
   NfcTag tag = nfc.read();
   tag.print();
   tagId = tag.getUidString();
   Serial.println(tagId);
   if (tagId == "77 D6 FC 1B")
   {digitalWrite(27, HIGH);
   delay(1000);
   digitalWrite(27, LOW);
   delay(1000);
   }
   else
   {
   digitalWrite(27, HIGH);
   delay(200);
   digitalWrite(27, LOW);
   delay(200);
   digitalWrite(27, HIGH);
   delay(200);
   digitalWrite(27, LOW);
   delay(200);
   digitalWrite(27, HIGH);
   delay(200);
   digitalWrite(27, LOW);
   delay(200);
   digitalWrite(27, HIGH);
   delay(200);
   digitalWrite(27, LOW);
   delay(200);
   digitalWrite(27, HIGH);
   delay(200);
   digitalWrite(27, LOW);
   delay(200);
   }
 }
}