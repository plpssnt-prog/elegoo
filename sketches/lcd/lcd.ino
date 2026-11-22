// UNO Lab — progetto "lcd": display LCD 1602 (16 caratteri x 2 righe).
// Collegamenti (piedini numerati da 1 = VSS a 16 = K: i nomi sono stampati sul display):
//   1 VSS -> GND   2 VDD -> 5V   3 V0 -> piedino centrale del potenziometro (contrasto)
//   4 RS -> pin 7  5 RW -> GND   6 E -> pin 8
//   11 D4 -> pin 9   12 D5 -> pin 10   13 D6 -> pin 11   14 D7 -> pin 12
//   15 A -> resistenza 220 ohm -> 5V   16 K -> GND
//   potenziometro: piedini esterni -> 5V e GND
// Comandi: ID?  |  1<testo> riga 1  |  2<testo> riga 2  |  X pulisce
#include <Arduino.h>
#include <LiquidCrystal.h>

const char* ID = "lcd";
LiquidCrystal lcd(7, 8, 9, 10, 11, 12);

char buf[40];
byte len = 0;

void riga(int n, const char* t) {
  char r[17];
  int i = 0;
  for (; i < 16 && t[i]; i++) r[i] = t[i];
  for (; i < 16; i++) r[i] = ' ';
  r[16] = 0;
  lcd.setCursor(0, n);
  lcd.print(r);
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == '1' || c[0] == '2') { riga(c[0] - '1', c + 1); Serial.println("OK"); return; }
  if (c[0] == 'X') { lcd.clear(); Serial.println("OK"); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  lcd.begin(16, 2);
  riga(0, "UNO Lab");
  riga(1, "pronto!");
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
