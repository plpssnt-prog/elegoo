// UNO Lab — progetto "servo": servo SG90 + sensore a ultrasuoni HC-SR04.
// Collegamenti:
//   Servo:  marrone -> GND, rosso -> 5V, arancione -> pin 9
//   HC-SR04: Vcc -> 5V, Gnd -> GND, Trig -> pin 12, Echo -> pin 11
//   (5V e GND passano dalle righe + e – della breadboard)
// Comandi:
//   ID?        -> "ID servo"
//   A<gradi>   -> modalità manuale, servo all'angolo (0-180)
//   ?          -> "POS <gradi>"
//   D?         -> "D <cm>" (una misura)
//   S1 / S0    -> avvia/ferma invio continuo della distanza ("D <cm>")
//   M0         -> manuale    M1 -> radar ("R <gradi> <cm>")    M2 -> segui ("F <gradi> <cm>")
// Distanza: centimetri con un decimale, -1 se fuori portata.
#include <Arduino.h>
#include <Servo.h>

const char* ID = "servo";
const int PIN_SERVO = 9, PIN_TRIG = 12, PIN_ECHO = 11;
const int RADAR_MIN = 15, RADAR_MAX = 165, RADAR_PASSO = 3;

Servo servo;
int angolo = 90;
int modo = 0;              // 0 manuale, 1 radar, 2 segui
bool invioDistanza = false;
int dirRadar = 1;
unsigned long ultimo = 0;
char buf[24];
byte len = 0;

float misura() {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);
  unsigned long us = pulseIn(PIN_ECHO, HIGH, 25000UL);   // ~4 m al massimo
  if (us == 0) return -1;
  return us / 58.0;
}

void stampaCm(float cm) {
  if (cm < 0) Serial.println(-1);
  else Serial.println(cm, 1);
}

void muovi(int a) {
  angolo = constrain(a, 0, 180);
  servo.write(angolo);
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (strcmp(c, "D?") == 0) { Serial.print("D "); stampaCm(misura()); return; }
  if (c[0] == 'A') {
    int v = atoi(c + 1);
    if (v < 0 || v > 180) { Serial.println("ERR range"); return; }
    modo = 0;
    muovi(v);
    Serial.print("OK "); Serial.println(angolo);
    return;
  }
  if (c[0] == '?') { Serial.print("POS "); Serial.println(angolo); return; }
  if (c[0] == 'S') { invioDistanza = (c[1] == '1'); Serial.println(invioDistanza ? "OK S1" : "OK S0"); return; }
  if (c[0] == 'M') {
    int m = c[1] - '0';
    if (m < 0 || m > 2) { Serial.println("ERR range"); return; }
    modo = m;
    if (modo == 1) { muovi(RADAR_MIN); dirRadar = 1; ultimo = millis() + 300; }
    Serial.print("OK M"); Serial.println(modo);
    return;
  }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  Serial.begin(115200);
  servo.attach(PIN_SERVO);
  muovi(90);
  Serial.print("READY "); Serial.println(ID);
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }

  unsigned long ora = millis();
  if ((long)(ora - ultimo) < 0) return;

  if (modo == 1) {                     // radar: misura, poi avanza di un passo
    if (ora - ultimo < 45) return;
    ultimo = ora;
    float cm = misura();
    Serial.print("R "); Serial.print(angolo); Serial.print(' '); stampaCm(cm);
    int prossimo = angolo + dirRadar * RADAR_PASSO;
    if (prossimo > RADAR_MAX || prossimo < RADAR_MIN) { dirRadar = -dirRadar; prossimo = angolo + dirRadar * RADAR_PASSO; }
    muovi(prossimo);
  } else if (modo == 2) {              // segui: 5 cm -> 0°, 40 cm -> 180°
    if (ora - ultimo < 80) return;
    ultimo = ora;
    float cm = misura();
    if (cm > 0) {
      int a = map((long)(constrain(cm, 5, 40) * 10), 50, 400, 0, 180);
      angolo = (angolo * 2 + a) / 3;   // movimento più morbido
      servo.write(angolo);
    }
    Serial.print("F "); Serial.print(angolo); Serial.print(' '); stampaCm(cm);
  } else if (invioDistanza) {          // manuale con distanza in tempo reale
    if (ora - ultimo < 150) return;
    ultimo = ora;
    Serial.print("D "); stampaCm(misura());
  }
}
