// UNO Lab — progetto "servo": servo SG90 sul pin 9.
// Collegamenti: marrone -> GND, rosso -> 5V, arancione -> pin 9
// Comandi: ID?  |  A<gradi> (0-180)  |  ?  (posizione attuale)
#include <Arduino.h>
#include <Servo.h>

const char* ID = "servo";
const int PIN = 9;

Servo servo;
int angolo = 90;
char buf[24];
byte len = 0;

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == 'A') {
    int v = atoi(c + 1);
    if (v < 0 || v > 180) { Serial.println("ERR range"); return; }
    angolo = v;
    servo.write(angolo);
    Serial.print("OK "); Serial.println(angolo);
    return;
  }
  if (c[0] == '?') { Serial.print("POS "); Serial.println(angolo); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  Serial.begin(115200);
  servo.attach(PIN);
  servo.write(angolo);
  Serial.print("READY "); Serial.println(ID);
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
}
