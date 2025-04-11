
int HALL = 33;
int PIR = 32;
int PIR_LED = 27;
int HALL_LED = 14;
void setup() {
  Serial.begin(115200);
  pinMode(PIR, INPUT_PULLUP);
  pinMode(HALL, INPUT_PULLUP);
  pinMode(PIR_LED, OUTPUT);
  pinMode(HALL_LED, OUTPUT);
  digitalWrite(PIR_LED, LOW);
  digitalWrite(HALL_LED, LOW);
}

void loop() {
  if (digitalRead(PIR) == HIGH ) {
    digitalWrite(PIR_LED, HIGH);
    Serial.println("PIR ON");
  } 
  else
  {
    digitalWrite(PIR_LED, LOW);
    Serial.println("PIR OFF");
  }

  if (digitalRead(HALL) == LOW)
  {
    digitalWrite(HALL_LED, LOW);
    Serial.println("HALL ON");
  }
  else
  {
    digitalWrite(HALL_LED, HIGH);
    Serial.println("HALL OFF");
  }
  delay(100);
}
