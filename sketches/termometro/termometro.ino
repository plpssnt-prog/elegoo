// UNO Lab — progetto "termometro": DHT11 + display LCD. Funziona anche senza telefono.
// Collegamenti:
//   display LCD esattamente come nel progetto "lcd" (RS 7, E 8, D4-D7 9-12, potenziometro del contrasto)
//   DHT11: S -> pin 2, + -> riga +, – -> riga –
// Riga 1: temperatura e umidità attuali. Riga 2: minima e massima da quando è acceso.
// Invio: "T <temp> <umidità> <min> <max>"
#include <Arduino.h>
#include <LiquidCrystal.h>

const char* ID = "termometro";
const int PIN_DHT = 2;
LiquidCrystal lcd(7, 8, 9, 10, 11, 12);

int tMin = 100, tMax = -100;
unsigned long t0 = 0;
char buf[24];
byte len = 0;

long attendi(int livello, unsigned long maxUs) {
  unsigned long t = micros();
  while (digitalRead(PIN_DHT) == livello) if (micros() - t > maxUs) return -1;
  return micros() - t;
}

bool leggiDHT(int& temp, int& umid) {
  byte d[5] = { 0, 0, 0, 0, 0 };
  pinMode(PIN_DHT, OUTPUT); digitalWrite(PIN_DHT, LOW); delay(20);
  pinMode(PIN_DHT, INPUT_PULLUP);
  if (attendi(HIGH, 200) < 0 || attendi(LOW, 120) < 0 || attendi(HIGH, 120) < 0) return false;
  for (int i = 0; i < 40; i++) {
    if (attendi(LOW, 100) < 0) return false;
    long alto = attendi(HIGH, 120);
    if (alto < 0) return false;
    d[i / 8] = (d[i / 8] << 1) | (alto > 45 ? 1 : 0);
  }
  if (((d[0] + d[1] + d[2] + d[3]) & 0xFF) != d[4]) return false;
  umid = d[0]; temp = d[2];
  return true;
}

void aggiorna() {
  int t, h;
  lcd.setCursor(0, 0);
  if (!leggiDHT(t, h)) {
    lcd.print("Sensore assente ");
    Serial.println("T -99 -99 -99 -99");
    return;
  }
  tMin = min(tMin, t); tMax = max(tMax, t);
  char r[17];
  snprintf(r, 17, "%3d%cC  Umid %2d%% ", t, (char)223, h);   // 223 = simbolo dei gradi sull'LCD
  lcd.print(r);
  lcd.setCursor(0, 1);
  snprintf(r, 17, "min %2d  max %2d  ", tMin, tMax);
  lcd.print(r);
  Serial.print("T "); Serial.print(t); Serial.print(' '); Serial.print(h); Serial.print(' ');
  Serial.print(tMin); Serial.print(' '); Serial.println(tMax);
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == 'Z') { tMin = 100; tMax = -100; aggiorna(); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  lcd.begin(16, 2);
  lcd.print("Termometro");
  lcd.setCursor(0, 1); lcd.print("avvio...");
  pinMode(PIN_DHT, INPUT_PULLUP);
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
  t0 = millis() - 1000;
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  if (millis() - t0 >= 2000) { t0 = millis(); aggiorna(); }
}
