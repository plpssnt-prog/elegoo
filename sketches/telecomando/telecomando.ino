// UNO Lab — progetto "telecomando": ricevitore infrarossi + telecomando del kit (protocollo NEC).
// Collegamenti (cavetti maschio-femmina):
//   ricevitore: G (o -) -> GND,  R (centrale) -> 5V,  Y (o S) -> pin 11
// Il LED "L" lampeggia quando arriva un tasto.
// Comandi: ID?
// Invio: "K <codice esadecimale>" per ogni tasto,  "R" quando il tasto resta premuto
#include <Arduino.h>

const char* ID = "telecomando";
const int PIN_IR = 11;

char buf[24];
byte len = 0;
unsigned long ledFino = 0;

// durata in microsecondi del livello attuale (0 se supera il limite)
unsigned long durata(int livello, unsigned long maxUs) {
  unsigned long t = micros();
  while (digitalRead(PIN_IR) == livello) {
    if (micros() - t > maxUs) return 0;
  }
  return micros() - t;
}

void leggiNEC() {
  unsigned long basso = durata(LOW, 11000);
  if (basso < 7000) return;                    // non è l'inizio di un messaggio NEC
  unsigned long alto = durata(HIGH, 6000);
  if (alto > 1700 && alto < 2800) { Serial.println("R"); return; }   // ripetizione
  if (alto < 3500) return;
  unsigned long codice = 0;
  for (int i = 0; i < 32; i++) {
    if (durata(LOW, 1000) == 0) return;
    unsigned long h = durata(HIGH, 2500);
    if (h == 0) return;
    codice = (codice << 1) | (h > 1000 ? 1 : 0);
  }
  Serial.print("K "); Serial.println(codice, HEX);
  digitalWrite(13, HIGH); ledFino = millis() + 120;
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(PIN_IR, INPUT);
  pinMode(13, OUTPUT);
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  if (digitalRead(PIN_IR) == LOW) leggiNEC();
  if (ledFino && millis() > ledFino) { digitalWrite(13, LOW); ledFino = 0; }
}
