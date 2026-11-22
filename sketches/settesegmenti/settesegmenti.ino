// UNO Lab — progetto "settesegmenti": display a 7 segmenti (1 cifra, catodo comune) con il 74HC595.
// Collegamenti del chip come nel progetto "registro":
//   16 VCC, 10 MR -> 5V   8 GND, 13 OE -> GND   14 DS -> pin 12   12 latch -> pin 11   11 clock -> pin 9
// Uscite del chip -> resistenza 220 ohm -> segmento del display:
//   Q0 -> a   Q1 -> b   Q2 -> c   Q3 -> d   Q4 -> e   Q5 -> f   Q6 -> g   Q7 -> punto (dp)
// Display (punto in basso a destra): piedini centrali 3 e 8 (comune) -> GND
//   in alto da sinistra: 10 g, 9 f, 8 comune, 7 a, 6 b    in basso da sinistra: 1 e, 2 d, 3 comune, 4 c, 5 dp
// Comandi: ID?  |  D<carattere> (0-9, A-F, -, spazio)  |  .1/.0 punto  |  C<n> conto alla rovescia da n
//          |  R lancio del dado  |  E spegne
// Invio: "S <carattere>" a ogni cambio, "FINE" alla fine del conto alla rovescia
#include <Arduino.h>

const char* ID = "settesegmenti";
const int DS = 12, LATCH = 11, CLK = 9;

const char CAR[] = "0123456789ABCDEF- ";
const byte SEG[] = { 0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F,
                     0x77, 0x7C, 0x39, 0x5E, 0x79, 0x71, 0x40, 0x00 };
char attuale = ' ';
bool punto = false;
int conto = -1, dado = 0;
unsigned long t0 = 0;
char buf[24];
byte len = 0;

void mostra(char c) {
  const char* p = strchr(CAR, toupper(c));
  if (!p) return;
  attuale = toupper(c);
  byte v = SEG[p - CAR] | (punto ? 0x80 : 0);
  digitalWrite(LATCH, LOW);
  shiftOut(DS, CLK, MSBFIRST, v);
  digitalWrite(LATCH, HIGH);
  Serial.print("S "); Serial.println(attuale);
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == 'D') { conto = -1; dado = 0; mostra(c[1] ? c[1] : ' '); return; }
  if (c[0] == '.') { punto = (c[1] == '1'); mostra(attuale); return; }
  if (c[0] == 'C') { conto = constrain(atoi(c + 1), 1, 9); dado = 0; t0 = millis(); mostra('0' + conto); return; }
  if (c[0] == 'R') { conto = -1; dado = 12; t0 = millis(); return; }
  if (c[0] == 'E') { conto = -1; dado = 0; punto = false; mostra(' '); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(DS, OUTPUT); pinMode(LATCH, OUTPUT); pinMode(CLK, OUTPUT);
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
  randomSeed(analogRead(A5));
  mostra('-');
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  unsigned long ora = millis();
  if (conto > 0 && ora - t0 >= 1000) {
    t0 = ora; conto--;
    mostra('0' + conto);
    if (conto == 0) { Serial.println("FINE"); conto = -1; }
  }
  if (dado > 0 && ora - t0 >= 70 + (12 - dado) * 25) {   // rallenta come un dado che si ferma
    t0 = ora; dado--;
    mostra('1' + random(6));
  }
}
