// UNO Lab — progetto "simon": il gioco della memoria. Funziona anche senza telefono.
// Collegamenti:
//   LED rosso -> pin 2, verde -> pin 3, blu -> pin 4, giallo -> pin 5 (piedino corto -> 220 ohm -> riga –)
//   pulsanti (un piedino al pin, quello opposto in diagonale -> riga –):
//     rosso -> pin 6, verde -> pin 7, blu -> pin 8, giallo -> pin 9
//   buzzer PASSIVO: + -> pin 10, altro -> riga –
// Gioco: la UNO accende una sequenza di luci, tu la ripeti con i pulsanti. Ogni turno si allunga di uno.
// Premi un pulsante qualsiasi per iniziare. Il record resta salvato anche spegnendo.
// Invio: "S <stato> <livello> <record>"  stato: 0 attesa, 1 la UNO mostra, 2 tocca a te, 3 errore
#include <Arduino.h>
#include <EEPROM.h>

const char* ID = "simon";
const int LED[4] = { 2, 3, 4, 5 }, BTN[4] = { 6, 7, 8, 9 }, BUZ = 10;
const int NOTA[4] = { 262, 330, 392, 523 };

byte seq[64];
int lung = 0, record = 0;
char buf[24];
byte len = 0;

void stato(int s) {
  Serial.print("S "); Serial.print(s); Serial.print(' '); Serial.print(lung); Serial.print(' '); Serial.println(record);
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == 'Z') { record = 0; EEPROM.update(0, 0); stato(0); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void leggiSeriale() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
}

void luce(int i, int ms) {
  digitalWrite(LED[i], HIGH); tone(BUZ, NOTA[i]);
  delay(ms);
  digitalWrite(LED[i], LOW); noTone(BUZ);
}

int attendiTasto(unsigned long maxMs) {     // ritorna 0-3, oppure -1 se scade il tempo
  unsigned long t0 = millis();
  while (millis() - t0 < maxMs) {
    leggiSeriale();
    for (int i = 0; i < 4; i++) {
      if (digitalRead(BTN[i]) == LOW) {
        digitalWrite(LED[i], HIGH); tone(BUZ, NOTA[i]);
        delay(20);
        while (digitalRead(BTN[i]) == LOW) leggiSeriale();
        delay(20);
        digitalWrite(LED[i], LOW); noTone(BUZ);
        return i;
      }
    }
  }
  return -1;
}

void sconfitta() {
  stato(3);
  for (int f = 400; f > 100; f -= 30) { tone(BUZ, f); delay(30); }
  noTone(BUZ);
  for (int k = 0; k < 3; k++) {
    for (int i = 0; i < 4; i++) digitalWrite(LED[i], HIGH);
    delay(200);
    for (int i = 0; i < 4; i++) digitalWrite(LED[i], LOW);
    delay(200);
  }
}

void setup() {
  for (int i = 0; i < 4; i++) { pinMode(LED[i], OUTPUT); pinMode(BTN[i], INPUT_PULLUP); }
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
  record = EEPROM.read(0);
  if (record > 64) record = 0;
  randomSeed(analogRead(A5) ^ micros());
  stato(0);
}

void loop() {
  // attesa: luci che girano finché non premi un pulsante
  lung = 0;
  stato(0);
  int k = 0;
  while (true) {
    leggiSeriale();
    digitalWrite(LED[k % 4], HIGH); delay(120); digitalWrite(LED[k % 4], LOW);
    k++;
    bool premuto = false;
    for (int i = 0; i < 4; i++) if (digitalRead(BTN[i]) == LOW) premuto = true;
    if (premuto) break;
  }
  while (attendiTasto(50) >= 0) {}
  randomSeed(micros());
  delay(600);

  while (true) {
    seq[lung++] = random(4);
    stato(1);
    int ms = max(180, 500 - lung * 20);       // sempre più veloce
    for (int i = 0; i < lung; i++) { luce(seq[i], ms); delay(ms / 2); }
    stato(2);
    for (int i = 0; i < lung; i++) {
      int t = attendiTasto(4000);
      if (t != seq[i]) {
        lung--;                                // livello raggiunto
        if (lung > record) { record = lung; EEPROM.update(0, record); }
        sconfitta();
        return;
      }
    }
    if (lung >= 64) { lung--; return; }
    delay(500);
  }
}
