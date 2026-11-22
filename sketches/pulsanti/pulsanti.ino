// UNO Lab — progetto "pulsanti": 2 pulsanti e il sensore di inclinazione (tilt).
// Collegamenti (resistenze interne di pull-up, non servono resistenze):
//   pulsante A: un piedino -> pin 2, piedino opposto in diagonale -> GND
//   pulsante B: un piedino -> pin 3, piedino opposto in diagonale -> GND
//   sensore di inclinazione: un piedino -> pin 4, l'altro -> GND
// Il LED "L" sulla scheda si accende quando premi A.
// Comandi: ID?  |  ?
// Invio: "B <a><b><t>" a ogni cambio (1 = premuto / inclinazione chiusa)
#include <Arduino.h>

const char* ID = "pulsanti";
const int PA = 2, PB = 3, PT = 4;

byte stato = 255, letto = 255;
unsigned long cambio = 0;
char buf[24];
byte len = 0;

byte leggi() {
  return (digitalRead(PA) == LOW ? 4 : 0) | (digitalRead(PB) == LOW ? 2 : 0) | (digitalRead(PT) == LOW ? 1 : 0);
}

void invia() {
  Serial.print("B ");
  Serial.print((stato >> 2) & 1); Serial.print((stato >> 1) & 1); Serial.println(stato & 1);
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == '?') { invia(); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(PA, INPUT_PULLUP); pinMode(PB, INPUT_PULLUP); pinMode(PT, INPUT_PULLUP);
  pinMode(13, OUTPUT);
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  byte v = leggi();
  if (v != letto) { letto = v; cambio = millis(); }
  if (letto != stato && millis() - cambio > 25) {   // antirimbalzo
    stato = letto;
    digitalWrite(13, (stato >> 2) & 1);
    invia();
  }
}
