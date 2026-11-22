// UNO Lab — progetto "lampada": luce notturna automatica. Funziona anche senza telefono.
// Collegamenti:
//   fotoresistenza: riga + -> fotoresistenza -> A0 -> resistenza 10 kohm -> riga –
//   potenziometro (sensibilità): esterni -> riga + e riga –, centrale -> A1
//   2 LED bianchi -> pin 9 e pin 10 (piedino corto -> 220 ohm -> riga –)
//   5V della UNO -> riga +, GND -> riga –
// Quando la luce scende sotto la soglia scelta con la manopola, i LED si accendono piano piano.
// Invio: "L <luce 0-1023> <soglia 0-1023> <luminosità LED 0-255>"
#include <Arduino.h>

const char* ID = "lampada";
const int LDR = A0, POT = A1, L1 = 9, L2 = 10;

float media = 512;
int liv = 0;
unsigned long t0 = 0, tInvio = 0;
char buf[24];
byte len = 0;

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(L1, OUTPUT); pinMode(L2, OUTPUT);
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
  media = analogRead(LDR);
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  if (millis() - t0 < 20) return;
  t0 = millis();
  media = media * 0.9 + analogRead(LDR) * 0.1;          // ignora le ombre veloci
  int soglia = analogRead(POT);
  int obiettivo = 0;
  if (media < soglia) obiettivo = constrain(map((long)(soglia - media), 0, 150, 40, 255), 40, 255);
  if (liv < obiettivo) liv++;                             // accensione e spegnimento dolci
  else if (liv > obiettivo) liv--;
  analogWrite(L1, liv); analogWrite(L2, liv);
  if (millis() - tInvio > 200) {
    tInvio = millis();
    Serial.print("L "); Serial.print((int)media); Serial.print(' '); Serial.print(soglia); Serial.print(' '); Serial.println(liv);
  }
}
