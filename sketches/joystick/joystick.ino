// UNO Lab — progetto "joystick": modulo joystick a 2 assi con pulsante.
// Collegamenti (cavetti maschio-femmina, niente breadboard):
//   GND -> GND   +5V -> 5V   VRx -> A0   VRy -> A1   SW -> pin 2
// Comandi: ID?  |  ?
// Invio: "J <x 0-1023> <y 0-1023> <pulsante 0/1>" quando cambia (e ogni mezzo secondo)
#include <Arduino.h>

const char* ID = "joystick";
const int PX = A0, PY = A1, PSW = 2;

int ux = -100, uy = -100, ub = -1;
unsigned long t0 = 0, tInvio = 0;
char buf[24];
byte len = 0;

void invia(int x, int y, int b) {
  ux = x; uy = y; ub = b; tInvio = millis();
  Serial.print("J "); Serial.print(x); Serial.print(' '); Serial.print(y); Serial.print(' '); Serial.println(b);
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == '?') { invia(analogRead(PX), analogRead(PY), digitalRead(PSW) == LOW); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(PSW, INPUT_PULLUP);
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  if (millis() - t0 < 40) return;
  t0 = millis();
  int x = analogRead(PX), y = analogRead(PY), b = digitalRead(PSW) == LOW;
  if (abs(x - ux) > 4 || abs(y - uy) > 4 || b != ub || millis() - tInvio > 500) invia(x, y, b);
}
