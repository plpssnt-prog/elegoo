// UNO Lab — progetto "termostato": il ventilatore si accende da solo quando fa caldo. Funziona anche a batteria.
// Alimentazione: modulo di alimentazione sulla breadboard (ponticelli su 5V) con la batteria 9V.
// Collegamenti:
//   relè comandato dal transistor come nel progetto "rele": pin 7 -> 1 kohm -> base; E -> riga –;
//     C -> bobina; altra bobina -> riga +; diodo sulla bobina con la striscia verso +
//   relè: COM -> riga +, NO -> un filo del motore; altro filo del motore -> riga –
//   DHT11: S -> pin 2, + -> riga +, – -> riga –
//   potenziometro (soglia): esterni -> riga + e riga –, centrale -> A0
//   GND della UNO -> riga – (massa comune). NON collegare il 5V della UNO.
// La manopola sceglie la soglia da 15 a 35 °C. Sopra la soglia il relè accende il ventilatore,
// sotto la soglia lo spegne (con 1 grado di margine per non farlo scattare di continuo).
// Il LED "L" della scheda è acceso quando il ventilatore è acceso.
// Comandi: ID?  |  M0 automatico, M1 sempre acceso, M2 sempre spento
// Invio: "T <temp> <umid> <soglia> <ventola 0/1> <modo>"
#include <Arduino.h>

const char* ID = "termostato";
const int PIN_DHT = 2, PIN_POT = A0, PIN_RELE = 7;

int temp = -99, umid = -99, soglia = 25, modo = 0;
bool ventola = false;
unsigned long t0 = 0;
char buf[24];
byte len = 0;

long attendi(int livello, unsigned long maxUs) {
  unsigned long t = micros();
  while (digitalRead(PIN_DHT) == livello) if (micros() - t > maxUs) return -1;
  return micros() - t;
}

bool leggiDHT(int& t, int& h) {
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
  h = d[0]; t = d[2];
  return true;
}

void decidi() {
  bool v = ventola;
  if (modo == 1) v = true;
  else if (modo == 2) v = false;
  else if (temp > -50) {
    if (temp >= soglia + 1) v = true;
    else if (temp <= soglia - 1) v = false;
  } else v = false;                              // sensore assente: per sicurezza spento
  ventola = v;
  digitalWrite(PIN_RELE, ventola);
  digitalWrite(13, ventola);
}

void invia() {
  Serial.print("T "); Serial.print(temp); Serial.print(' '); Serial.print(umid); Serial.print(' ');
  Serial.print(soglia); Serial.print(' '); Serial.print(ventola); Serial.print(' '); Serial.println(modo);
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == 'M') { modo = constrain(c[1] - '0', 0, 2); decidi(); invia(); return; }
  if (c[0] == '?') { invia(); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(PIN_RELE, OUTPUT); pinMode(13, OUTPUT);
  pinMode(PIN_DHT, INPUT_PULLUP);
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
  t0 = millis() - 1500;
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  if (millis() - t0 >= 2000) {
    t0 = millis();
    soglia = map(analogRead(PIN_POT), 0, 1023, 15, 35);
    int t, h;
    if (leggiDHT(t, h)) { temp = t; umid = h; } else { temp = umid = -99; }
    decidi();
    invia();
  }
}
