// UNO Lab — progetto "cronometro": cronometro su display a 4 cifre. Funziona anche senza telefono.
// Collegamenti:
//   chip 74HC595 come nel progetto "registro": 16 e 10 -> +, 8 e 13 -> –, 14 -> pin 12, 12 -> pin 11, 11 -> pin 9
//   uscite del chip -> resistenza 1 kohm -> segmenti del display (1k protegge i pin delle cifre): Q0 a, Q1 b, Q2 c, Q3 d, Q4 e, Q5 f, Q6 g, Q7 punto
//   display (punti in basso): piedini in alto da sinistra 12 D1, 11 a, 10 f, 9 D2, 8 D3, 7 b
//                             piedini in basso da sinistra 1 e, 2 d, 3 punto, 4 c, 5 g, 6 D4
//   cifre D1 -> pin 2, D2 -> pin 3, D3 -> pin 4, D4 -> pin 5
//   pulsante avvia/ferma -> pin 6, pulsante azzera -> pin 7 (piedino opposto in diagonale -> riga –)
// Mostra secondi e centesimi fino a 99.99, poi minuti e secondi.
// Comandi: ID?  |  S avvia/ferma  |  Z azzera  |  K1/K0 display ad anodo comune sì/no (resta salvato)
// Invio: "C <millisecondi> <in corsa 0/1>"
#include <Arduino.h>
#include <EEPROM.h>

const char* ID = "cronometro";
const int DS = 12, LATCH = 11, CLK = 9, DIG[4] = { 2, 3, 4, 5 }, B_SS = 6, B_Z = 7;
const byte SEG[10] = { 0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F };

bool anodo = false, corre = false;
unsigned long base = 0, accum = 0, tInvio = 0;
byte cifre[4] = { 0x3F, 0x3F, 0x3F, 0x3F };
int quale = 0;
bool p1 = false, p2 = false;
unsigned long tTasti = 0;
char buf[24];
byte len = 0;

unsigned long tempo() { return accum + (corre ? millis() - base : 0); }

void avviaFerma() {
  if (corre) { accum += millis() - base; corre = false; }
  else { base = millis(); corre = true; }
}
void azzera() { accum = 0; base = millis(); }

void calcola() {
  unsigned long t = tempo();
  int v[4]; int punto;
  if (t < 100000UL) {                 // SS.cc
    unsigned long cs = t / 10;
    v[0] = cs / 1000 % 10; v[1] = cs / 100 % 10; v[2] = cs / 10 % 10; v[3] = cs % 10; punto = 1;
  } else {                            // MM.SS
    unsigned long s = t / 1000, m = s / 60 % 100; s %= 60;
    v[0] = m / 10; v[1] = m % 10; v[2] = s / 10; v[3] = s % 10; punto = 1;
  }
  for (int i = 0; i < 4; i++) cifre[i] = SEG[v[i]] | (i == punto ? 0x80 : 0);
  if (v[0] == 0) cifre[0] = 0;        // niente zero iniziale
}

void multiplex() {                    // accende una cifra alla volta, molto velocemente
  for (int i = 0; i < 4; i++) digitalWrite(DIG[i], anodo ? LOW : HIGH);   // tutte spente
  byte s = anodo ? ~cifre[quale] : cifre[quale];
  digitalWrite(LATCH, LOW); shiftOut(DS, CLK, MSBFIRST, s); digitalWrite(LATCH, HIGH);
  digitalWrite(DIG[quale], anodo ? HIGH : LOW);
  quale = (quale + 1) % 4;
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == 'S') { avviaFerma(); return; }
  if (c[0] == 'Z') { azzera(); return; }
  if (c[0] == 'K') { anodo = (c[1] == '1'); EEPROM.update(2, anodo); Serial.println("OK"); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(DS, OUTPUT); pinMode(LATCH, OUTPUT); pinMode(CLK, OUTPUT);
  for (int i = 0; i < 4; i++) pinMode(DIG[i], OUTPUT);
  pinMode(B_SS, INPUT_PULLUP); pinMode(B_Z, INPUT_PULLUP);
  anodo = EEPROM.read(2) == 1;
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
  if (ora - tTasti >= 15) {           // pulsanti con antirimbalzo
    tTasti = ora;
    bool a = digitalRead(B_SS) == LOW, b = digitalRead(B_Z) == LOW;
    if (a && !p1) avviaFerma();
    if (b && !p2) azzera();
    p1 = a; p2 = b;
  }
  calcola();
  multiplex();
  delayMicroseconds(1500);
  if (ora - tInvio >= 200) {
    tInvio = ora;
    Serial.print("C "); Serial.print(tempo()); Serial.print(' '); Serial.println(corre);
  }
}
