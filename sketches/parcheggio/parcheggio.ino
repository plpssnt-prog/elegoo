// UNO Lab — progetto "parcheggio": sensore di parcheggio come in auto. Funziona anche senza telefono.
// Collegamenti:
//   HC-SR04: Vcc -> riga +, Gnd -> riga –, Trig -> pin 12, Echo -> pin 11
//   buzzer PASSIVO: piedino + -> pin 8, altro -> riga –
//   LED verde -> pin 5, giallo -> pin 6, rosso -> pin 7 (piedino corto -> 220 ohm -> riga –)
//   5V della UNO -> riga +, GND -> riga –
// Oltre 50 cm: verde e silenzio. 50-20 cm: giallo, bip sempre più veloci. Sotto 20: rosso. Sotto 8: suono continuo.
// Invio: "D <cm> <zona 0-3>" (cm = -1 se fuori portata)
#include <Arduino.h>

const char* ID = "parcheggio";
const int TRIG = 12, ECHO = 11, BUZ = 8, LV = 5, LG = 6, LR = 7;

float cm = -1;
unsigned long tMisura = 0, tBip = 0;
bool bipOn = false;
char buf[24];
byte len = 0;

float misura() {
  digitalWrite(TRIG, LOW); delayMicroseconds(2);
  digitalWrite(TRIG, HIGH); delayMicroseconds(10); digitalWrite(TRIG, LOW);
  unsigned long us = pulseIn(ECHO, HIGH, 25000UL);
  return us == 0 ? -1 : us / 58.0;
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(TRIG, OUTPUT); pinMode(ECHO, INPUT);
  pinMode(LV, OUTPUT); pinMode(LG, OUTPUT); pinMode(LR, OUTPUT);
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  unsigned long ora = millis();
  if (ora - tMisura >= 80) {
    tMisura = ora;
    float m = misura();
    cm = (m < 0) ? -1 : (cm < 0 ? m : cm * 0.6 + m * 0.4);   // un po' di media, meno salti
    int zona = (cm < 0 || cm > 50) ? 0 : cm > 20 ? 1 : cm > 8 ? 2 : 3;
    digitalWrite(LV, zona == 0); digitalWrite(LG, zona == 1); digitalWrite(LR, zona >= 2);
    static byte n = 0;
    if (++n % 2 == 0) { Serial.print("D "); Serial.print(cm, 1); Serial.print(' '); Serial.println(zona); }
  }
  // bip: intervallo proporzionale alla distanza
  if (cm < 0 || cm > 50) { noTone(BUZ); bipOn = false; return; }
  if (cm <= 8) { tone(BUZ, 1500); bipOn = true; return; }
  unsigned long pausa = map((long)cm, 8, 50, 60, 600);
  if (!bipOn && ora - tBip >= pausa) { tone(BUZ, 1500); bipOn = true; tBip = ora; }
  else if (bipOn && ora - tBip >= 60) { noTone(BUZ); bipOn = false; tBip = ora; }
}
