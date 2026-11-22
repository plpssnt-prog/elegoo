// UNO Lab — progetto "servoir": servo comandato dal telecomando IR. Funziona anche senza telefono.
// Collegamenti (bordo della breadboard per 5V e GND):
//   5V della UNO -> riga +, GND -> riga –
//   servo: rosso -> riga +, marrone -> riga –, arancione -> pin 9
//   ricevitore IR: G -> riga –, R -> riga +, Y -> pin 11
// Tasti: 0-9 -> angolo (0 = 0°, 9 = 180°)   ⏮ / ⏭ -> -10° / +10°   VOL- / VOL+ -> -1° / +1°
//        ⏯ -> avvia/ferma il movimento automatico   ⏻ -> torna al centro (90°)
// Invio: "A <angolo> <auto 0/1>"
#include <Arduino.h>
#include <Servo.h>

const char* ID = "servoir";
const int PIN_IR = 11, PIN_SERVO = 9;

Servo servo;
int angolo = 90, dir = 2;
bool automatico = false;
unsigned long ultimoCodice = 0, tAuto = 0;
char buf[24];
byte len = 0;

unsigned long durata(int livello, unsigned long maxUs) {
  unsigned long t = micros();
  while (digitalRead(PIN_IR) == livello) if (micros() - t > maxUs) return 0;
  return micros() - t;
}

// ritorna il codice NEC, 1 per "ripeti", 0 se non valido
unsigned long leggiNEC() {
  if (durata(LOW, 11000) < 7000) return 0;
  unsigned long alto = durata(HIGH, 6000);
  if (alto > 1700 && alto < 2800) return 1;
  if (alto < 3500) return 0;
  unsigned long codice = 0;
  for (int i = 0; i < 32; i++) {
    if (durata(LOW, 1000) == 0) return 0;
    unsigned long h = durata(HIGH, 2500);
    if (h == 0) return 0;
    codice = (codice << 1) | (h > 1000 ? 1 : 0);
  }
  return codice;
}

void vai(int a) {
  angolo = constrain(a, 0, 180);
  servo.write(angolo);
  Serial.print("A "); Serial.print(angolo); Serial.print(' '); Serial.println(automatico);
}

void tasto(unsigned long k, bool ripeti) {
  switch (k) {
    case 0xFF22DD: vai(angolo - 10); break;      // ⏮
    case 0xFFC23D: vai(angolo + 10); break;      // ⏭
    case 0xFFA857: vai(angolo - 1); break;       // VOL-
    case 0xFF629D: vai(angolo + 1); break;       // VOL+
    case 0xFF02FD: if (!ripeti) { automatico = !automatico; vai(angolo); } break;   // ⏯
    case 0xFFA25D: if (!ripeti) { automatico = false; vai(90); } break;            // ⏻
    default: {
      const unsigned long N[10] = { 0xFF6897, 0xFF30CF, 0xFF18E7, 0xFF7A85, 0xFF10EF,
                                    0xFF38C7, 0xFF5AA5, 0xFF42BD, 0xFF4AB5, 0xFF52AD };
      for (int i = 0; i < 10; i++) if (k == N[i] && !ripeti) { automatico = false; vai(i * 20); }
    }
  }
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == '?') { vai(angolo); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(PIN_IR, INPUT);
  Serial.begin(115200);
  servo.attach(PIN_SERVO);
  servo.write(angolo);
  Serial.print("READY "); Serial.println(ID);
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  if (digitalRead(PIN_IR) == LOW) {
    unsigned long k = leggiNEC();
    if (k == 1 && ultimoCodice) tasto(ultimoCodice, true);
    else if (k > 1) { ultimoCodice = k; tasto(k, false); }
  }
  if (automatico && millis() - tAuto > 30) {
    tAuto = millis();
    if (angolo + dir > 180 || angolo + dir < 0) dir = -dir;
    angolo += dir;
    servo.write(angolo);
  }
}
