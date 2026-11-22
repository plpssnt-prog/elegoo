// UNO Lab — progetto "potenziometro": manopola su A0 e LED sul pin 9.
// Collegamenti:
//   potenziometro: piedino esterno -> 5V, piedino centrale -> A0, altro esterno -> GND
//   LED: piedino lungo -> pin 9, piedino corto -> resistenza 220 ohm -> GND
// Comandi: ID?  |  M0 la manopola regola il LED  |  M1 il LED lo regola l'app  |  P<0-255>  |  S1/S0 invio valori
// Invio: "V <0-1023> <luminosità 0-255>"
#include <Arduino.h>

const char* ID = "potenziometro";
const int PIN_POT = A0, PIN_LED = 9;

int modo = 0, luce = 0, ultimoV = -100;
bool invio = true;
unsigned long t0 = 0, tInvio = 0;
char buf[24];
byte len = 0;

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == 'M') { modo = (c[1] == '1'); Serial.print("M "); Serial.println(modo); return; }
  if (c[0] == 'P') { modo = 1; luce = constrain(atoi(c + 1), 0, 255); analogWrite(PIN_LED, luce); Serial.println("M 1"); return; }
  if (c[0] == 'S') { invio = (c[1] == '1'); Serial.println("OK"); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(PIN_LED, OUTPUT);
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  if (millis() - t0 < 40) return;
  t0 = millis();
  int v = analogRead(PIN_POT);
  if (modo == 0) { luce = v / 4; analogWrite(PIN_LED, luce); }
  // invia quando il valore cambia, e comunque ogni mezzo secondo
  if (invio && (abs(v - ultimoV) > 2 || millis() - tInvio > 500)) {
    ultimoV = v; tInvio = millis();
    Serial.print("V "); Serial.print(v); Serial.print(' '); Serial.println(luce);
  }
}
