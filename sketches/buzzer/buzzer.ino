// UNO Lab — progetto "buzzer": buzzer PASSIVO sul pin 8.
// Collegamenti: piedino + del buzzer -> pin 8, l'altro -> GND
// (il buzzer passivo è quello senza adesivo, con il circuito verde visibile sotto)
// Comandi: ID?  |  T<freq>,<ms> (31-5000 Hz, 10-3000 ms)  |  X (stop)
#include <Arduino.h>

const char* ID = "buzzer";
const int PIN = 8;

char buf[24];
byte len = 0;

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == 'T') {
    long f = atol(c + 1);
    char* p = strchr(c, ',');
    long d = p ? atol(p + 1) : 200;
    if (f < 31 || f > 5000 || d < 10 || d > 3000) { Serial.println("ERR range"); return; }
    tone(PIN, f, d);
    Serial.println("OK");
    return;
  }
  if (c[0] == 'X') { noTone(PIN); Serial.println("OK"); return; }
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
}
