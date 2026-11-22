// UNO Lab — progetto "passo": motore passo-passo 28BYJ-48 con il modulo driver ULN2003.
// Alimentazione: modulo di alimentazione sulla breadboard (5V) con batteria 9V.
// Collegamenti (cavetti maschio-femmina):
//   IN1 -> pin 8   IN2 -> pin 9   IN3 -> pin 10   IN4 -> pin 11
//   + del driver -> riga + (5V del modulo)   - del driver -> riga –   GND della UNO -> riga –
//   motore: connettore bianco nella presa del driver (entra solo in un verso)
// Comandi: ID?  |  G<gradi> vai all'angolo  |  R<gradi> ruota di (+ orario, - antiorario)
//          |  V<giri/min 1-15>  |  Z imposta lo zero qui  |  X ferma e rilascia
// Invio: "P <gradi>" durante il movimento, "FERMO <gradi>" all'arrivo
#include <Arduino.h>

const char* ID = "passo";
const int PIN[4] = { 8, 9, 10, 11 };
const long PASSI_GIRO = 4096;                 // mezzi passi per un giro dell'albero
const byte SEQ[8] = { 0b1000, 0b1100, 0b0100, 0b0110, 0b0010, 0b0011, 0b0001, 0b1001 };

long pos = 0, obiettivo = 0;
unsigned long intervallo = 2000, tPasso = 0, tInvio = 0;
bool inMoto = false;
char buf[24];
byte len = 0;

void bobine(byte b) { for (int i = 0; i < 4; i++) digitalWrite(PIN[i], (b >> (3 - i)) & 1); }
float gradi() { return pos * 360.0 / PASSI_GIRO; }

void velocita(int rpm) {
  rpm = constrain(rpm, 1, 15);
  intervallo = 60000000UL / ((unsigned long)rpm * PASSI_GIRO);
  Serial.print("V "); Serial.println(rpm);
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == 'G') { obiettivo = (long)(atof(c + 1) * PASSI_GIRO / 360.0); inMoto = true; return; }
  if (c[0] == 'R') { obiettivo = pos + (long)(atof(c + 1) * PASSI_GIRO / 360.0); inMoto = true; return; }
  if (c[0] == 'V') { velocita(atoi(c + 1)); return; }
  if (c[0] == 'Z') { pos = obiettivo = 0; Serial.println("FERMO 0.0"); return; }
  if (c[0] == 'X') { obiettivo = pos; inMoto = false; bobine(0); Serial.print("FERMO "); Serial.println(gradi(), 1); return; }
  if (c[0] == '?') { Serial.print("P "); Serial.println(gradi(), 1); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  for (int i = 0; i < 4; i++) pinMode(PIN[i], OUTPUT);
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
  velocita(10);
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  if (!inMoto) return;
  unsigned long ora = micros();
  if (pos == obiettivo) {
    inMoto = false;
    bobine(0);                                  // spegne le bobine: il motore non scalda
    Serial.print("FERMO "); Serial.println(gradi(), 1);
    return;
  }
  if (ora - tPasso >= intervallo) {
    tPasso = ora;
    pos += (obiettivo > pos) ? 1 : -1;
    bobine(SEQ[((pos % 8) + 8) % 8]);
  }
  if (millis() - tInvio > 100) { tInvio = millis(); Serial.print("P "); Serial.println(gradi(), 1); }
}
