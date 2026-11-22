// UNO Lab — progetto "dado": scuoti la breadboard e il display tira un dado. Funziona anche senza telefono.
// Collegamenti:
//   chip 74HC595 e display a 7 segmenti esattamente come nel progetto "settesegmenti"
//   sensore di inclinazione: un piedino -> pin 2, l'altro -> riga –
// Comandi: ID?  |  R tira  |  K1/K0 display ad anodo comune sì/no (resta salvato)
// Invio: "N <numero>" a fine lancio, "L" quando parte il lancio
#include <Arduino.h>
#include <EEPROM.h>

const char* ID = "dado";
const int DS = 12, LATCH = 11, CLK = 9, TILT = 2;
const byte CIFRA[7] = { 0x00, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D };   // 1..6

bool anodo = false;
int scosse = 0, ultimo = -1, giro = 0;
unsigned long tScossa = 0, tGiro = 0;
char buf[24];
byte len = 0;

void scrivi(byte v) {
  if (anodo) v = ~v;
  digitalWrite(LATCH, LOW); shiftOut(DS, CLK, MSBFIRST, v); digitalWrite(LATCH, HIGH);
}

void lancia() { giro = 14; tGiro = 0; Serial.println("L"); }

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == 'R') { lancia(); return; }
  if (c[0] == 'K') { anodo = (c[1] == '1'); EEPROM.update(1, anodo); scrivi(0x40); Serial.println("OK"); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(DS, OUTPUT); pinMode(LATCH, OUTPUT); pinMode(CLK, OUTPUT);
  pinMode(TILT, INPUT_PULLUP);
  anodo = EEPROM.read(1) == 1;
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
  randomSeed(analogRead(A5));
  scrivi(0x40);                     // trattino
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  unsigned long ora = millis();
  // scossa: il sensore cambia stato più volte in poco tempo
  int v = digitalRead(TILT);
  if (v != ultimo) {
    ultimo = v;
    if (ora - tScossa > 30) {                // ignora i rimbalzi della pallina
      if (ora - tScossa > 700) scosse = 0;
      tScossa = ora;
      if (++scosse >= 3 && giro == 0) { scosse = 0; lancia(); }
    }
  }
  if (giro > 0 && ora - tGiro >= 60UL + (14 - giro) * 22) {
    tGiro = ora;
    int n = random(1, 7);
    scrivi(CIFRA[n]);
    if (--giro == 0) { Serial.print("N "); Serial.println(n); randomSeed(micros()); }
  }
}
