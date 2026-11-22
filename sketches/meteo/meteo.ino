// UNO Lab — progetto "meteo": modulo DHT11 (temperatura e umidità) + termistore.
// Collegamenti:
//   DHT11: S -> pin 2, + (centrale) -> 5V, - -> GND
//   termistore: 5V -> termistore -> A0 -> resistenza 10 kohm -> GND
// Comandi: ID?  |  ?  (misura subito)
// Invio ogni 2 s: "T <temp DHT11> <umidità %> <temp termistore>"  (-99 = lettura non riuscita)
#include <Arduino.h>
#include <math.h>

const char* ID = "meteo";
const int PIN_DHT = 2, PIN_TERM = A0;

unsigned long t0 = 0;
char buf[24];
byte len = 0;

long attendi(int livello, unsigned long maxUs) {
  unsigned long t = micros();
  while (digitalRead(PIN_DHT) == livello) {
    if (micros() - t > maxUs) return -1;
  }
  return micros() - t;
}

bool leggiDHT(int& temp, int& umid) {
  byte d[5] = { 0, 0, 0, 0, 0 };
  pinMode(PIN_DHT, OUTPUT);
  digitalWrite(PIN_DHT, LOW);
  delay(20);
  pinMode(PIN_DHT, INPUT_PULLUP);
  if (attendi(HIGH, 200) < 0) return false;   // il sensore risponde abbassando la linea
  if (attendi(LOW, 120) < 0) return false;
  if (attendi(HIGH, 120) < 0) return false;
  for (int i = 0; i < 40; i++) {
    if (attendi(LOW, 100) < 0) return false;
    long alto = attendi(HIGH, 120);
    if (alto < 0) return false;
    d[i / 8] = (d[i / 8] << 1) | (alto > 45 ? 1 : 0);
  }
  if (((d[0] + d[1] + d[2] + d[3]) & 0xFF) != d[4]) return false;
  umid = d[0];
  temp = d[2];
  return true;
}

float tempTermistore() {
  int a = analogRead(PIN_TERM);
  if (a <= 0 || a >= 1023) return -99;
  float r = 10000.0 * (1023.0 / a - 1.0);           // termistore verso 5V, 10k verso GND
  float invT = 1.0 / 298.15 + log(r / 10000.0) / 3950.0;
  return 1.0 / invT - 273.15;
}

void misura() {
  int t = -99, h = -99;
  if (!leggiDHT(t, h)) { t = -99; h = -99; }
  Serial.print("T "); Serial.print(t); Serial.print(' '); Serial.print(h); Serial.print(' ');
  Serial.println(tempTermistore(), 1);
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == '?') { misura(); t0 = millis(); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(PIN_DHT, INPUT_PULLUP);
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
  t0 = millis() - 1000;
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  if (millis() - t0 >= 2000) { t0 = millis(); misura(); }
}
