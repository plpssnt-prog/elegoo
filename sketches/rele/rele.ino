// UNO Lab — progetto "rele": un relè, l'interruttore comandato dalla UNO.
// La bobina del relè consuma circa 70 mA, troppo per un pin: la comanda il transistor PN2222.
// Collegamenti:
//   pin 7 -> resistenza 1 kohm -> base (B) del transistor; emettitore (E) -> riga –
//   collettore (C) -> un piedino della bobina del relè; l'altro piedino della bobina -> riga +
//   diodo tra i due piedini della bobina, con la striscia verso la riga + (protegge il transistor)
//   relè: COM -> riga +, NO -> LED verde, NC -> LED rosso (piedino corto -> 220 ohm -> riga –)
// A relè spento è acceso il rosso (NC), a relè acceso il verde (NO). Si sente il "clic".
// Comandi: ID?  |  R1 acceso, R0 spento  |  T<secondi> acceso per un po'  |  L<ms> lampeggio (500-5000), L0 stop
// Invio: "R <0/1> <secondi rimasti> <lampeggio ms>"
#include <Arduino.h>

const char* ID = "rele";
const int PIN = 7;

bool acceso = false;
unsigned long fine = 0, periodo = 0, tLamp = 0, tInvio = 0;
char buf[24];
byte len = 0;

void stato() {
  long resto = fine ? ((long)(fine - millis()) + 999) / 1000 : 0;
  if (resto < 0) resto = 0;
  Serial.print("R "); Serial.print(acceso); Serial.print(' '); Serial.print(resto); Serial.print(' '); Serial.println(periodo);
}

void imposta(bool on) {
  acceso = on;
  digitalWrite(PIN, on);
  digitalWrite(13, on);
  stato();
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == 'R') { fine = 0; periodo = 0; imposta(c[1] == '1'); return; }
  if (c[0] == 'T') {
    long s = constrain(atol(c + 1), 1, 3600);
    periodo = 0; fine = millis() + s * 1000UL;
    imposta(true);
    return;
  }
  if (c[0] == 'L') {
    long ms = atol(c + 1);
    fine = 0;
    periodo = ms == 0 ? 0 : constrain(ms, 500, 5000);   // il relè è meccanico: non troppo veloce
    tLamp = millis();
    if (!periodo) imposta(false); else stato();
    return;
  }
  if (c[0] == '?') { stato(); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(PIN, OUTPUT); pinMode(13, OUTPUT);
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
  imposta(false);
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  unsigned long ora = millis();
  if (fine && (long)(ora - fine) >= 0) { fine = 0; imposta(false); }
  if (periodo && ora - tLamp >= periodo / 2) { tLamp = ora; imposta(!acceso); }
  if (fine && ora - tInvio >= 1000) { tInvio = ora; stato(); }
}
