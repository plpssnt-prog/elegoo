// UNO Lab — progetto "luce": fotoresistenza su A0 (partitore con resistenza 10k).
// Collegamenti:
//   5V -> fotoresistenza -> A0
//   A0 -> resistenza 10 kohm -> GND
// Comandi: ID?  |  S1 / S0 (avvia/ferma invio)  |  R<ms> (intervallo 50-2000)
// Invio: "V <0-1023>"
#include <Arduino.h>

const char* ID = "luce";
const int PIN = A0;

char buf[24];
byte len = 0;
bool invio = true;
unsigned long intervallo = 100, ultimo = 0;

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == 'S') { invio = (c[1] == '1'); Serial.println(invio ? "OK S1" : "OK S0"); return; }
  if (c[0] == 'R') {
    long v = atol(c + 1);
    if (v < 50 || v > 2000) { Serial.println("ERR range"); return; }
    intervallo = v;
    Serial.print("OK R"); Serial.println(intervallo);
    return;
  }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  if (invio && millis() - ultimo >= intervallo) {
    ultimo = millis();
    Serial.print("V "); Serial.println(analogRead(PIN));
  }
}
