// UNO Lab — progetto "stazione": termometro + metro sullo stesso display LCD. Funziona anche a batteria.
// Collegamenti:
//   display LCD come nel progetto "lcd" (RS 7, E 8, D4-D7 9-12), potenziometro del contrasto
//   DHT11: S -> pin 2, + -> riga +, – -> riga –
//   HC-SR04: Vcc -> riga +, Gnd -> riga –, Trig -> pin 3, Echo -> pin 4
//   pulsante "pagina" (con due cavetti maschio-femmina): un piedino -> pin 5, quello opposto in diagonale -> riga –
//   LED verde -> A0, giallo -> A1, rosso -> A2 (i pin analogici usati come uscite; piedino corto -> 220 ohm -> riga –)
// Il pulsante cambia la pagina del display: meteo <-> distanza. I LED mostrano sempre la distanza:
//   verde oltre 50 cm (o niente davanti), giallo 50-20 cm, rosso sotto 20 cm.
// Comandi: ID?  |  P0 pagina meteo, P1 pagina distanza  |  Z azzera minima e massima
// Invio: "T <temp> <umid> <min> <max>"  "D <cm> <zona 0-2>"  "P <pagina>"
#include <Arduino.h>
#include <LiquidCrystal.h>

const char* ID = "stazione";
const int PIN_DHT = 2, TRIG = 3, ECHO = 4, BTN = 5, LV = A0, LG = A1, LR = A2;
LiquidCrystal lcd(7, 8, 9, 10, 11, 12);

int pagina = 0;
int temp = -99, umid = -99, tMin = 100, tMax = -100;
float cm = -1;
int zona = 0;
bool prima = false;
unsigned long tDht = 0, tDist = 0, tTasto = 0;
char buf[24];
byte len = 0;

// ---------------- DHT11
long attendi(int livello, unsigned long maxUs) {
  unsigned long t = micros();
  while (digitalRead(PIN_DHT) == livello) if (micros() - t > maxUs) return -1;
  return micros() - t;
}

bool leggiDHT(int& t, int& h) {
  byte d[5] = { 0, 0, 0, 0, 0 };
  pinMode(PIN_DHT, OUTPUT); digitalWrite(PIN_DHT, LOW); delay(20);
  pinMode(PIN_DHT, INPUT_PULLUP);
  if (attendi(HIGH, 200) < 0 || attendi(LOW, 120) < 0 || attendi(HIGH, 120) < 0) return false;
  for (int i = 0; i < 40; i++) {
    if (attendi(LOW, 100) < 0) return false;
    long alto = attendi(HIGH, 120);
    if (alto < 0) return false;
    d[i / 8] = (d[i / 8] << 1) | (alto > 45 ? 1 : 0);
  }
  if (((d[0] + d[1] + d[2] + d[3]) & 0xFF) != d[4]) return false;
  h = d[0]; t = d[2];
  return true;
}

// ---------------- HC-SR04
float misura() {
  digitalWrite(TRIG, LOW); delayMicroseconds(2);
  digitalWrite(TRIG, HIGH); delayMicroseconds(10); digitalWrite(TRIG, LOW);
  unsigned long us = pulseIn(ECHO, HIGH, 25000UL);
  return us == 0 ? -1 : us / 58.0;
}

// ---------------- display
void riga(int n, const char* t) {
  char r[17];
  int i = 0;
  for (; i < 16 && t[i]; i++) r[i] = t[i];
  for (; i < 16; i++) r[i] = ' ';
  r[16] = 0;
  lcd.setCursor(0, n);
  lcd.print(r);
}

void disegna() {
  char r[17];
  if (pagina == 0) {
    if (temp < -50) { riga(0, "Meteo: sensore"); riga(1, "non risponde"); return; }
    snprintf(r, 17, "%3d%cC  Umid %2d%%", temp, (char)223, umid);   // 223 = simbolo dei gradi
    riga(0, r);
    snprintf(r, 17, "min %2d  max %2d", tMin, tMax);
    riga(1, r);
  } else {
    if (cm < 0) riga(0, "Distanza: --");
    else {
      int intero = (int)cm, dec = (int)((cm - intero) * 10);
      snprintf(r, 17, "Dist %3d.%d cm", intero, dec);
      riga(0, r);
    }
    int n = cm < 0 ? 0 : constrain((int)(cm / 200.0 * 16 + 0.5), 0, 16);   // barra: 16 caratteri = 2 m
    for (int i = 0; i < 16; i++) r[i] = i < n ? (char)255 : ' ';
    r[16] = 0;
    lcd.setCursor(0, 1); lcd.print(r);
  }
}

void cambiaPagina(int p) {
  pagina = p;
  lcd.clear();
  disegna();
  Serial.print("P "); Serial.println(pagina);
}

void comando(char* c) {
  if (strcmp(c, "ID?") == 0) { Serial.print("ID "); Serial.println(ID); return; }
  if (c[0] == 'P') { cambiaPagina(c[1] == '1' ? 1 : 0); return; }
  if (c[0] == 'Z') { tMin = 100; tMax = -100; if (temp > -50) { tMin = tMax = temp; } disegna(); Serial.println("OK"); return; }
  if (c[0]) Serial.println("ERR cmd");
}

void setup() {
  pinMode(TRIG, OUTPUT); pinMode(ECHO, INPUT); pinMode(BTN, INPUT_PULLUP);
  pinMode(LV, OUTPUT); pinMode(LG, OUTPUT); pinMode(LR, OUTPUT);
  pinMode(PIN_DHT, INPUT_PULLUP);
  lcd.begin(16, 2);
  riga(0, "Stazione UNO Lab");
  riga(1, "avvio...");
  Serial.begin(115200);
  Serial.print("READY "); Serial.println(ID);
  Serial.print("P "); Serial.println(pagina);
  tDht = millis() - 1500;
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { buf[len] = 0; comando(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
  }
  unsigned long ora = millis();

  // pulsante: cambia pagina alla pressione (con antirimbalzo)
  if (ora - tTasto >= 20) {
    tTasto = ora;
    bool p = digitalRead(BTN) == LOW;
    if (p && !prima) cambiaPagina(1 - pagina);
    prima = p;
  }

  // distanza e LED, sempre (anche quando il display mostra il meteo)
  if (ora - tDist >= 150) {
    tDist = ora;
    float m = misura();
    cm = (m < 0) ? -1 : (cm < 0 ? m : cm * 0.6 + m * 0.4);
    zona = (cm < 0 || cm > 50) ? 0 : cm > 20 ? 1 : 2;
    digitalWrite(LV, zona == 0); digitalWrite(LG, zona == 1); digitalWrite(LR, zona == 2);
    if (pagina == 1) disegna();
    Serial.print("D "); Serial.print(cm, 1); Serial.print(' '); Serial.println(zona);
  }

  // temperatura e umidità ogni 2 secondi
  if (ora - tDht >= 2000) {
    tDht = ora;
    int t, h;
    if (leggiDHT(t, h)) {
      temp = t; umid = h;
      tMin = min(tMin, t); tMax = max(tMax, t);
    } else {
      temp = umid = -99;
    }
    if (pagina == 0) disegna();
    Serial.print("T "); Serial.print(temp); Serial.print(' '); Serial.print(umid); Serial.print(' ');
    Serial.print(tMin); Serial.print(' '); Serial.println(tMax);
  }
}
