// UNO Lab — progetto "blink": LED integrato (L, pin 13). Nessun collegamento.
// Comandi: ID?  |  L1 / L0 (acceso/spento fisso)  |  B<ms> (lampeggio, periodo 50-5000 ms)
#include <Arduino.h>

const char* ID = "blink";
const int LED = 13;

char buf[24];
byte len = 0;
unsigned long periodo = 500;   // 0 = lampeggio fermo
unsigned long ultimo = 0;
bool stato = false;

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == 'L') {
    periodo = 0;
    stato = (c[1] == '1');
    digitalWrite(LED, stato);
    Serial.println(stato ? "OK L1" : "OK L0");
    return;
  }
  if (c[0] == 'B') {
    long v = atol(c + 1);
    if (v < 50 || v > 5000) { Serial.println("ERR range"); return; }
    periodo = v;
    Serial.print("OK B"); Serial.println(periodo);
    return;
  }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(LED, OUTPUT);
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  if (periodo && millis() - ultimo >= periodo / 2) {
    ultimo = millis();
    stato = !stato;
    digitalWrite(LED, stato);
  }
}
