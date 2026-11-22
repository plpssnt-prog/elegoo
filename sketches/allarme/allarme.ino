// UNO Lab — progetto "allarme": sensore di inclinazione + buzzer ATTIVO + LED rosso.
// Collegamenti:
//   sensore di inclinazione: un piedino -> pin 2, l'altro -> GND
//   buzzer attivo (quello con l'adesivo): piedino lungo (+) -> pin 8, corto -> GND
//   LED rosso: piedino lungo -> pin 12, corto -> resistenza 220 ohm -> GND
// Comandi: ID?  |  A1 attiva, A0 disattiva (e spegne la sirena)  |  T prova sirena  |  ?
// Invio: "S <attivo> <allarme> <inclinazione>" a ogni cambio
#include <Arduino.h>

const char* ID = "allarme";
const int PT = 2, PBZ = 8, PLED = 12;

bool attivo = false, allarme = false;
int tilt = -1, letto = -1, base = -1;
unsigned long cambio = 0, tSirena = 0, fineProva = 0;
bool fase = false;
char buf[24];
byte len = 0;

void stato() {
  Serial.print("S "); Serial.print(attivo); Serial.print(' ');
  Serial.print(allarme); Serial.print(' '); Serial.println(tilt);
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == 'A') {
    attivo = (c[1] == '1');
    allarme = false;
    base = tilt;               // posizione di riferimento al momento dell'attivazione
    stato();
    return;
  }
  if (c[0] == 'T') { fineProva = millis() + 400; Serial.println("OK"); return; }
  if (c[0] == '?') { stato(); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(PT, INPUT_PULLUP);
  pinMode(PBZ, OUTPUT); pinMode(PLED, OUTPUT);
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
  int v = digitalRead(PT) == LOW;
  if (v != letto) { letto = v; cambio = ora; }
  if (letto != tilt && ora - cambio > 40) {
    tilt = letto;
    if (attivo && !allarme && tilt != base) allarme = true;
    stato();
  }
  if (allarme) {
    if (ora - tSirena > 200) { tSirena = ora; fase = !fase; }
    digitalWrite(PBZ, fase); digitalWrite(PLED, fase);
  } else {
    bool prova = (long)(fineProva - ora) > 0;
    digitalWrite(PBZ, prova);
    // LED: fisso se attivo, spento se disattivo
    digitalWrite(PLED, attivo || prova);
  }
}
