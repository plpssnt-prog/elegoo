// UNO Lab — progetto "metro": metro a ultrasuoni con display LCD. Funziona anche senza telefono.
// Collegamenti:
//   display LCD esattamente come nel progetto "lcd" (RS 7, E 8, D4-D7 9-12, potenziometro del contrasto)
//   HC-SR04: Vcc -> riga +, Gnd -> riga –, Trig -> pin 2, Echo -> pin 3
//   pulsante "blocca" (con due cavetti maschio-femmina): un piedino -> pin 4, quello opposto in diagonale -> riga –
// Il pulsante blocca la misura sul display (premi di nuovo per sbloccare).
// Invio: "D <cm> <bloccato 0/1>"
#include <Arduino.h>
#include <LiquidCrystal.h>

const char* ID = "metro";
const int TRIG = 2, ECHO = 3, BTN = 4;
LiquidCrystal lcd(7, 8, 9, 10, 11, 12);

float cm = -1;
bool bloccato = false, prima = false;
unsigned long t0 = 0;
char buf[24];
byte len = 0;

float misura() {
  digitalWrite(TRIG, LOW); delayMicroseconds(2);
  digitalWrite(TRIG, HIGH); delayMicroseconds(10); digitalWrite(TRIG, LOW);
  unsigned long us = pulseIn(ECHO, HIGH, 25000UL);
  return us == 0 ? -1 : us / 58.0;
}

void mostra() {
  char r[17];
  lcd.setCursor(0, 0);
  if (cm < 0) snprintf(r, 17, "Fuori portata   ");
  else {
    int intero = (int)cm, dec = (int)((cm - intero) * 10);
    snprintf(r, 17, "%3d.%d cm  %s", intero, dec, bloccato ? "[STOP]" : "      ");
  }
  lcd.print(r);
  // barra: 16 caratteri = 2 metri
  lcd.setCursor(0, 1);
  int n = cm < 0 ? 0 : constrain((int)(cm / 200.0 * 16 + 0.5), 0, 16);
  for (int i = 0; i < 16; i++) lcd.write(i < n ? (char)255 : ' ');
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == 'B') { bloccato = !bloccato; mostra(); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(TRIG, OUTPUT); pinMode(ECHO, INPUT); pinMode(BTN, INPUT_PULLUP);
  lcd.begin(16, 2);
  lcd.print("Metro UNO Lab");
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  bool p = digitalRead(BTN) == LOW;
  if (p && !prima) { bloccato = !bloccato; mostra(); delay(30); }
  prima = p;
  if (millis() - t0 < 200) return;
  t0 = millis();
  if (!bloccato) {
    float m = misura();
    cm = (m < 0) ? -1 : (cm < 0 ? m : cm * 0.5 + m * 0.5);
  }
  mostra();
  Serial.print("D "); Serial.print(cm, 1); Serial.print(' '); Serial.println(bloccato);
}
