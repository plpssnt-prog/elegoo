// UNO Lab — progetto "semaforo": 3 LED (rosso, giallo, verde).
// Collegamenti: ogni LED con il piedino lungo verso il pin, il corto verso GND, con resistenza 220 ohm.
//   rosso -> pin 12   giallo -> pin 11   verde -> pin 10
// Comandi: ID?  |  M0 manuale, M1 automatico, M2 giallo lampeggiante  |  L<r><y><g> es. L100  |  ?
// Invio: "S <r><y><g>" a ogni cambio
#include <Arduino.h>

const char* ID = "semaforo";
const int PR = 12, PY = 11, PG = 10;

int modo = 1, fase = 0;
bool r, y, g;
unsigned long t0 = 0;
char buf[24];
byte len = 0;

void luci(bool rr, bool yy, bool gg) {
  if (rr == r && yy == y && gg == g) return;
  r = rr; y = yy; g = gg;
  digitalWrite(PR, r); digitalWrite(PY, y); digitalWrite(PG, g);
  Serial.print("S "); Serial.print(r); Serial.print(y); Serial.println(g);
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == '?') { Serial.print("S "); Serial.print(r); Serial.print(y); Serial.println(g); Serial.print("M "); Serial.println(modo); return; }
  if (c[0] == 'M') {
    int m = c[1] - '0';
    if (m < 0 || m > 2) { Serial.println("ERR range"); return; }
    modo = m; fase = 0; t0 = 0;
    Serial.print("M "); Serial.println(modo);
    return;
  }
  if (c[0] == 'L' && strlen(c) >= 4) {
    modo = 0;
    Serial.println("M 0");
    luci(c[1] == '1', c[2] == '1', c[3] == '1');
    return;
  }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(PR, OUTPUT); pinMode(PY, OUTPUT); pinMode(PG, OUTPUT);
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
  r = y = g = true; luci(false, false, false);
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  unsigned long ora = millis();
  if (modo == 1) {
    // verde 4 s -> giallo 1,5 s -> rosso 4 s
    const unsigned long durata[3] = { 4000, 1500, 4000 };
    if (t0 == 0 || ora - t0 >= durata[fase]) {
      if (t0 != 0) fase = (fase + 1) % 3;
      t0 = ora;
      luci(fase == 2, fase == 1, fase == 0);
    }
  } else if (modo == 2) {
    if (ora - t0 >= 600) { t0 = ora; fase = !fase; luci(false, fase, false); }
  }
}
