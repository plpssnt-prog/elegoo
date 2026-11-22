// UNO Lab — progetto "rgb": LED RGB a catodo comune.
// Collegamenti (come nella lezione RGB del kit Elegoo):
//   piedino lungo (catodo) -> GND
//   rosso -> resistenza 220 ohm -> pin 6
//   verde -> resistenza 220 ohm -> pin 5
//   blu   -> resistenza 220 ohm -> pin 3
// Comandi: ID?  |  C<r>,<g>,<b>  (0-255 ciascuno)
#include <Arduino.h>

const char* ID = "rgb";
const int PIN_R = 6, PIN_G = 5, PIN_B = 3;

char buf[24];
byte len = 0;

void colore(int r, int g, int b) {
  analogWrite(PIN_R, r);
  analogWrite(PIN_G, g);
  analogWrite(PIN_B, b);
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == 'C') {
    int r = 0, g = 0, b = 0;
    char* p = c + 1;
    r = atoi(p);
    p = strchr(p, ','); if (!p) { Serial.println("ERR fmt"); return; }
    g = atoi(++p);
    p = strchr(p, ','); if (!p) { Serial.println("ERR fmt"); return; }
    b = atoi(++p);
    colore(constrain(r, 0, 255), constrain(g, 0, 255), constrain(b, 0, 255));
    Serial.println("OK");
    return;
  }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(PIN_R, OUTPUT);
  pinMode(PIN_G, OUTPUT);
  pinMode(PIN_B, OUTPUT);
  colore(0, 0, 0);
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
}
