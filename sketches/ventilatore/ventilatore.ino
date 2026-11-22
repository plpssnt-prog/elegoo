// UNO Lab — progetto "ventilatore": motorino con elica comandato dal chip L293D.
// Alimentazione motore: modulo di alimentazione sulla breadboard (ponticelli su 5V) con batteria 9V.
// Collegamenti del chip L293D (tacca a sinistra):
//   1 EN1 -> pin 5   2 IN1 -> pin 3   7 IN2 -> pin 4   3 OUT1 e 6 OUT2 -> i due fili del motore
//   4, 5, 12, 13 -> GND (riga –)   16 VCC1 -> 5V (riga +)   8 VCC2 -> 5V (riga +)
//   GND della UNO -> riga – (massa comune)
// Comandi: ID?  |  V<-100..100> velocità in % (negativo = senso inverso)  |  S stop
// Invio: "V <velocità>"
#include <Arduino.h>

const char* ID = "ventilatore";
const int EN = 5, IN1 = 3, IN2 = 4;

int vel = 0;
char buf[24];
byte len = 0;

void imposta(int v) {
  v = constrain(v, -100, 100);
  int pwm = v == 0 ? 0 : map(abs(v), 1, 100, 90, 255);   // sotto ~90 il motore non parte
  if (v != 0 && (vel == 0 || (v > 0) != (vel > 0))) {
    analogWrite(EN, 0);
    digitalWrite(IN1, v > 0); digitalWrite(IN2, v < 0);
    analogWrite(EN, 255); delay(80);                     // spinta iniziale
  }
  digitalWrite(IN1, v > 0); digitalWrite(IN2, v < 0);
  analogWrite(EN, pwm);
  vel = v;
  Serial.print("V "); Serial.println(vel);
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == 'V') { imposta(atoi(c + 1)); return; }
  if (c[0] == 'S') { imposta(0); return; }
  if (c[0] == '?') { Serial.print("V "); Serial.println(vel); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(EN, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
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
