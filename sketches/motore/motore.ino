// UNO Lab — progetto "motore": il motorino con l'elica comandato da un solo transistor.
// Più semplice del progetto con l'L293D: gira in un solo verso, ma la velocità si regola lo stesso.
// Alimentazione motore: modulo di alimentazione sulla breadboard (ponticelli su 5V) con la batteria 9V.
// Collegamenti:
//   pin 9 -> resistenza 1 kohm -> base (B) del PN2222; emettitore (E) -> riga –
//   collettore (C) -> un filo del motore; l'altro filo del motore -> riga +
//   diodo in parallelo al motore, con la striscia verso la riga +
//   GND della UNO -> riga – (massa comune). NON collegare il 5V della UNO.
// Comandi: ID?  |  V<0-100> velocità in %  |  S stop  |  P soffio (1 secondo al massimo)
// Invio: "V <velocità>"
#include <Arduino.h>

const char* ID = "motore";
const int PIN = 9;

int vel = 0;
unsigned long fineSoffio = 0;
char buf[24];
byte len = 0;

void imposta(int v) {
  v = constrain(v, 0, 100);
  if (v > 0 && vel == 0) { analogWrite(PIN, 255); delay(80); }   // spinta per partire
  analogWrite(PIN, v == 0 ? 0 : map(v, 1, 100, 70, 255));
  vel = v;
  Serial.print("V "); Serial.println(vel);
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == 'V') { fineSoffio = 0; imposta(atoi(c + 1)); return; }
  if (c[0] == 'S') { fineSoffio = 0; imposta(0); return; }
  if (c[0] == 'P') { imposta(100); fineSoffio = millis() + 1000; return; }
  if (c[0] == '?') { Serial.print("V "); Serial.println(vel); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(PIN, OUTPUT);
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  if (fineSoffio && (long)(millis() - fineSoffio) >= 0) { fineSoffio = 0; imposta(0); }
}
