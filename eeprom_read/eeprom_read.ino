#include <EEPROM.h>

void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    char command = Serial.read();

    if (command == 'R') {
      int address = Serial.parseInt();
      byte value = EEPROM.read(address);
      Serial.println(value);
    } else if (command == 'W') {
      int address = Serial.parseInt();
      byte value = Serial.parseInt();
      EEPROM.write(address, value);
      Serial.println("OK");
    } else if (command == 'r') {
      for (int i = 0; i < EEPROM.length(); i++) {
        byte value = EEPROM.read(i);
        Serial.print(i);
        Serial.print(":");
        Serial.println(value);
      }
    } else if (command == 'C') {
      for (int i = 0; i < EEPROM.length(); i++) {
        EEPROM.write(i, 0);
      }
      Serial.println("EEPROM cleared");
    } else if (command == 'A') {
      for (int i = 0; i < 6; i++) {
        int value = analogRead(i);
        Serial.println(value);
      }
      for (int i = 2; i < 14; i++) {
        int value = digitalRead(i);
        Serial.println(value);
      }
    }
  }
}
