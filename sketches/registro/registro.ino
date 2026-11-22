// UNO Lab — progetto "registro": 8 LED comandati da 3 pin con il chip 74HC595.
// Collegamenti del chip (tacca a sinistra):
//   16 VCC -> 5V   10 MR -> 5V   8 GND -> GND   13 OE -> GND
//   14 DS -> pin 12   12 ST_CP (latch) -> pin 11   11 SH_CP (clock) -> pin 9
//   uscite Q0 (15), Q1..Q7 (1..7) -> piedino lungo del LED; piedino corto -> resistenza 220 ohm -> GND
// Comandi: ID?  |  W<0-255> accende i LED secondo i bit  |  P<n> giochi di luce (0 stop, 1 supercar,
//          2 contatore, 3 casuale, 4 riempimento)  |  V<ms> velocità (30-1000)
// Invio: "S <0-255>" a ogni cambio
#include <Arduino.h>

const char* ID = "registro";
const int DS = 12, LATCH = 11, CLK = 9;

byte valore = 0;
int gioco = 1, passo = 0, dir = 1;
unsigned long vel = 120, t0 = 0;
char buf[24];
byte len = 0;

void scrivi(byte v) {
  valore = v;
  digitalWrite(LATCH, LOW);
  shiftOut(DS, CLK, MSBFIRST, v);
  digitalWrite(LATCH, HIGH);
  Serial.print("S "); Serial.println(v);
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == 'W') { gioco = 0; scrivi(constrain(atoi(c + 1), 0, 255)); return; }
  if (c[0] == 'P') { gioco = constrain(atoi(c + 1), 0, 4); passo = 0; dir = 1; Serial.print("P "); Serial.println(gioco); return; }
  if (c[0] == 'V') { vel = constrain(atol(c + 1), 30, 1000); Serial.println("OK"); return; }
  if (c[0] == '?') { Serial.print("S "); Serial.println(valore); Serial.print("P "); Serial.println(gioco); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(DS, OUTPUT); pinMode(LATCH, OUTPUT); pinMode(CLK, OUTPUT);
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
  randomSeed(analogRead(A5));
  scrivi(0);
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  if (gioco == 0 || millis() - t0 < vel) return;
  t0 = millis();
  switch (gioco) {
    case 1:   // supercar: una luce che va avanti e indietro
      scrivi(1 << passo);
      passo += dir;
      if (passo == 7 || passo == 0) dir = -dir;
      break;
    case 2: scrivi(passo++ & 0xFF); break;          // contatore binario
    case 3: scrivi(random(256)); break;
    case 4:   // riempimento e svuotamento
      scrivi(passo < 9 ? (1 << passo) - 1 : 0xFF << (passo - 8));
      passo = (passo + 1) % 17;
      break;
  }
}
