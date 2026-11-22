"""Genera una guida PDF per principiante per ogni progetto di UNO Lab."""
import sys, os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.utils import simpleSplit

pdfmetrics.registerFont(TTFont("S", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("SB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

W, H = A4
BROWN = HexColor("#7a4a21"); RED = HexColor("#d62828"); ORANGE = HexColor("#f28c18")
GREEN = HexColor("#2a9d3a"); BLUEW = HexColor("#1f5fd1"); YEL = HexColor("#d4a100")
BLK = HexColor("#222222"); BOARD = HexColor("#1d2630"); GREY = HexColor("#555b66")
LIGHT = HexColor("#eef1f5"); ACC = HexColor("#1f6fd1"); SERVO = HexColor("#2f6bd8")
WARN_BG = HexColor("#fff4d6"); WARN_FG = HexColor("#7a5a00")

c = None  # canvas corrente


# ------------------------------------------------------------------ testo
def text(x, y, s, size=10, font="S", color=black, anchor="l"):
    c.setFont(font, size); c.setFillColor(color)
    {"c": c.drawCentredString, "r": c.drawRightString}.get(anchor, c.drawString)(x, y, s)


def wrap(x, y, s, width, size=10.5, lead=14.5, font="S", color=black):
    for ln in simpleSplit(s, font, size, width):
        text(x, y, ln, size, font, color); y -= lead
    return y


def header(titolo, sotto, n, tot, num):
    c.setFillColor(HexColor("#0f1115")); c.rect(0, H - 78, W, 78, stroke=0, fill=1)
    text(40, H - 30, f"UNO LAB  ·  PROGETTO {num}", 8.5, "SB", HexColor("#7fb2ff"))
    text(40, H - 52, titolo, 20, "SB", white)
    text(40, H - 69, sotto, 10, "S", HexColor("#b8c0cc"))
    text(W - 40, 22, f"{titolo}  ·  pagina {n} di {tot}", 8, "S", GREY, "r")


def titolo_sez(x, y, s):
    text(x, y, s, 13, "SB"); return y - 22


def badge(x, y, n, col=ACC):
    c.setFillColor(col); c.circle(x, y, 10, stroke=0, fill=1)
    text(x, y - 4, str(n), 10.5, "SB", white, "c")


def riquadro(x, y, w, righe, bg=LIGHT, fg=black, titolo=None, size=9.8):
    # calcola altezza
    lines = []
    for r in righe:
        lines += simpleSplit(r, "S", size, w - 24) + [None]
    hh = 14 + (18 if titolo else 0) + sum(14 if l else 3 for l in lines)
    c.setFillColor(bg); c.roundRect(x, y - hh, w, hh, 7, stroke=0, fill=1)
    yy = y - 18
    if titolo:
        text(x + 12, yy, titolo, 10.5, "SB", fg); yy -= 18
    for l in lines:
        if l: text(x + 12, yy, l, size, "S", fg); yy -= 14
        else: yy -= 3
    return y - hh - 12


def passi(x, y, w, lista, start=1):
    for i, (tit, desc) in enumerate(lista, start):
        badge(x + 10, y + 4, i)
        y = wrap(x + 30, y, tit, w - 30, 10.5, 14, "SB")
        if desc:
            y = wrap(x + 30, y, desc, w - 30, 9.4, 12.5, "S", GREY)
        y -= 6
    return y


# ------------------------------------------------------------------ disegni
def pad(x, y, hl=None):
    c.setFillColor(HexColor("#0b0d10")); c.rect(x - 5, y - 5, 10, 10, stroke=0, fill=1)
    c.setFillColor(HexColor("#3a4350")); c.rect(x - 2.2, y - 2.2, 4.4, 4.4, stroke=0, fill=1)
    if hl:
        c.setStrokeColor(hl); c.setLineWidth(2.2); c.circle(x, y, 9, stroke=1, fill=0)


def uno(x0, y0, hl=None, s=1.0, led_l=False):
    hl = hl or {}
    w, h = 320 * s, 220 * s
    pins = {}
    c.setFillColor(BOARD); c.roundRect(x0, y0, w, h, 8, stroke=0, fill=1)
    c.setFillColor(HexColor("#c9ccd1")); c.rect(x0 - 22 * s, y0 + h - 95 * s, 60 * s, 50 * s, stroke=0, fill=1)
    text(x0 + 8 * s, y0 + h - 108 * s, "USB", 7 * s, "SB", white, "c")
    c.setFillColor(HexColor("#111111")); c.rect(x0 - 14 * s, y0 + 28 * s, 50 * s, 38 * s, stroke=0, fill=1)
    c.setFillColor(HexColor("#dddddd")); c.rect(x0 + 8 * s, y0 + h - 34 * s, 26 * s, 22 * s, stroke=0, fill=1)
    c.setFillColor(HexColor("#b33a2e")); c.circle(x0 + 21 * s, y0 + h - 23 * s, 6 * s, stroke=0, fill=1)
    text(x0 + 21 * s, y0 + h - 44 * s, "RESET", 5.5 * s, "S", HexColor("#9aa3ad"), "c")
    c.setFillColor(HexColor("#0a0a0a")); c.rect(x0 + 150 * s, y0 + 52 * s, 150 * s, 34 * s, stroke=0, fill=1)
    text(x0 + 225 * s, y0 + 66 * s, "ATMEGA328P", 7 * s, "S", HexColor("#777777"), "c")
    text(x0 + 225 * s, y0 + h - 100 * s, "ELEGOO", 17 * s, "SB", white, "c")
    text(x0 + 225 * s, y0 + h - 118 * s, "UNO R3", 12 * s, "SB", white, "c")
    # LED integrati L / TX / RX
    for i, (lab, col) in enumerate([("L", HexColor("#ffb020") if led_l else HexColor("#6b5a2a")),
                                    ("TX", HexColor("#5b6470")), ("RX", HexColor("#5b6470"))]):
        lx, ly = x0 + 112 * s, y0 + h - 62 * s - i * 13 * s
        c.setFillColor(col); c.rect(lx - 6 * s, ly - 3 * s, 12 * s, 6 * s, stroke=0, fill=1)
        text(lx - 10 * s, ly - 2.5 * s, lab, 6 * s, "S", HexColor("#cfd6de"), "r")
    text(x0 + 225 * s, y0 + h - 140 * s, "", 1)
    c.setFillColor(HexColor("#3ecf8e")); c.rect(x0 + 290 * s, y0 + h - 70 * s, 10 * s, 5 * s, stroke=0, fill=1)
    text(x0 + 288 * s, y0 + h - 69 * s, "ON", 6 * s, "S", HexColor("#cfd6de"), "r")

    step = 13 * s
    top = ["", "", "AREF", "GND", "13", "12", "~11", "~10", "~9", "8", None,
           "7", "~6", "~5", "4", "~3", "2", "1", "0"]
    px, py = x0 + 66 * s, y0 + h - 14 * s
    for lab in top:
        if lab is None: px += step * 0.6; continue
        key = lab.replace("~", "")
        k = "D" + key if key.isdigit() else ("GNDT" if key == "GND" else key)
        pad(px, py, hl.get(k))
        if lab:
            c.saveState(); c.translate(px + 2.5 * s, py - 10 * s); c.rotate(90)
            c.setFont("SB" if k in hl else "S", 6.5 * s)
            c.setFillColor(hl.get(k, HexColor("#cfd6de"))); c.drawRightString(0, 0, lab); c.restoreState()
            pins[k] = (px, py)
        px += step
    text(x0 + 200 * s, y0 + h - 58 * s, "DIGITAL (PWM~)", 7 * s, "S", HexColor("#cfd6de"), "c")
    bot = ["", "IOREF", "RESET", "3.3V", "5V", "GND", "GND2", "Vin", None, "A0", "A1", "A2", "A3", "A4", "A5"]
    px, py = x0 + 96 * s, y0 + 14 * s
    for lab in bot:
        if lab is None: px += step * 1.2; continue
        pad(px, py, hl.get(lab))
        if lab:
            c.saveState(); c.translate(px + 2.5 * s, py + 10 * s); c.rotate(90)
            c.setFont("SB" if lab in hl else "S", 6.5 * s)
            c.setFillColor(hl.get(lab, HexColor("#cfd6de")))
            c.drawString(0, 0, "GND" if lab == "GND2" else lab); c.restoreState()
            pins[lab] = (px, py)
        px += step
    text(x0 + 150 * s, y0 + 58 * s, "POWER", 7 * s, "S", HexColor("#cfd6de"), "c")
    text(x0 + 262 * s, y0 + 58 * s, "ANALOG IN", 7 * s, "S", HexColor("#cfd6de"), "c")
    return pins


SP = 16
RIGHE = "abcdefghij"
# Le lettere sono stampate al contrario rispetto alle posizioni del disegno, come sulla breadboard del kit
# tenuta con le righe a-e verso di sé (e accanto alla scanalatura). Le posizioni nel codice restano "a" = in alto.
ETICHETTA_RIGA = dict(zip("abcdefghij", "jihgfedcba"))


def breadboard(x0, y0, ncol=18, evid=None):
    """Mezza breadboard (righe a-j). Ritorna funzione foro(colonna, riga)."""
    w, h = ncol * SP + 44, 11 * SP + 52
    top = y0 + h - 26

    def foro(col, r):
        k = RIGHE.index(r)
        return (x0 + 30 + (col - 1) * SP, top - (k if k < 5 else k + 2) * SP)

    c.setFillColor(HexColor("#f6f6f3")); c.setStrokeColor(HexColor("#c8c8c0")); c.setLineWidth(1)
    c.roundRect(x0, y0, w, h, 6, stroke=1, fill=1)
    ce = (foro(1, "e")[1] + foro(1, "f")[1]) / 2
    c.setFillColor(HexColor("#e2e2dc")); c.rect(x0 + 6, ce - 5, w - 12, 10, stroke=0, fill=1)
    if evid:  # evidenzia strisce collegate
        for (col, half) in evid:
            ya, yb = (foro(col, "a")[1], foro(col, "e")[1]) if half == "top" else (foro(col, "f")[1], foro(col, "j")[1])
            x = foro(col, "a")[0]
            c.setStrokeColor(HexColor("#2a9d3a")); c.setFillColor(HexColor("#d6f5dc")); c.setLineWidth(1.5)
            c.roundRect(x - 6, yb - 6, 12, ya - yb + 12, 5, stroke=1, fill=1)
    for col in range(1, ncol + 1):
        for r in RIGHE:
            x, y = foro(col, r)
            c.setFillColor(HexColor("#9a9a92")); c.rect(x - 2, y - 2, 4, 4, stroke=0, fill=1)
        x, y = foro(col, "a")
        text(x, y + 9, str(col), 6, "S", GREY, "c")
        x, y = foro(col, "j")
        text(x, y - 15, str(col), 6, "S", GREY, "c")
    for r in RIGHE:
        x, y = foro(1, r)
        text(x - 12, y - 2.5, ETICHETTA_RIGA[r], 7, "S", GREY, "c")
    return foro


def wire(p0, p1, col, c1=None, c2=None, w=3.2):
    c.setStrokeColor(col); c.setLineWidth(w); c.setLineCap(1)
    if c1 is None: c.line(*p0, *p1)
    else: c.bezier(*p0, *c1, *c2, *p1)
    c.setFillColor(col)
    c.circle(*p0, 3.3, stroke=0, fill=1); c.circle(*p1, 3.3, stroke=0, fill=1)


def etichetta(x, y, s, col, anchor="c"):
    c.setFont("SB", 8.5)
    tw = c.stringWidth(s, "SB", 8.5)
    bx = x - tw / 2 - 4 if anchor == "c" else (x - tw - 8 if anchor == "r" else x)
    c.setFillColor(white); c.setStrokeColor(col); c.setLineWidth(1.2)
    c.roundRect(bx, y - 4, tw + 8, 14, 3, stroke=1, fill=1)
    text(bx + 4, y, s, 8.5, "SB", col)


def resistenza(p1, p2, bande):
    import math
    c.setStrokeColor(HexColor("#8a8a8a")); c.setLineWidth(1.6); c.line(*p1, *p2)
    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    ang = math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))
    c.saveState(); c.translate(mx, my); c.rotate(ang)
    c.setFillColor(HexColor("#d9c49a")); c.roundRect(-16, -5.5, 32, 11, 5, stroke=0, fill=1)
    for i, col in enumerate(bande):
        c.setFillColor(HexColor(col)); c.rect(-11 + i * 5, -5.5, 2.6, 11, stroke=0, fill=1)
    c.restoreState()
    c.setFillColor(HexColor("#8a8a8a")); c.circle(*p1, 2.2, stroke=0, fill=1); c.circle(*p2, 2.2, stroke=0, fill=1)


B220 = ["#d62828", "#d62828", "#111111", "#111111", "#7a4a21"]
B10K = ["#7a4a21", "#111111", "#111111", "#d62828", "#7a4a21"]


def resistenza_grande(x, y, bande, nome, desc):
    c.setStrokeColor(HexColor("#8a8a8a")); c.setLineWidth(2); c.line(x, y, x + 110, y)
    c.setFillColor(HexColor("#d9c49a")); c.roundRect(x + 30, y - 9, 50, 18, 8, stroke=0, fill=1)
    for i, col in enumerate(bande):
        c.setFillColor(HexColor(col)); c.rect(x + 36 + i * 8, y - 9, 4, 18, stroke=0, fill=1)
    text(x + 125, y + 2, nome, 10.5, "SB")
    text(x + 125, y - 11, desc, 8.8, "S", GREY)


def gambe(punti, base_y, col=HexColor("#9a9a9a"), w=1.8):
    c.setStrokeColor(col); c.setLineWidth(w)
    for (x, y) in punti: c.line(x, base_y, x, y)
    c.setFillColor(col)
    for (x, y) in punti: c.circle(x, y, 2.2, stroke=0, fill=1)


def mini_breadboard(x, y):
    """Spiegazione: come sono collegati i fori."""
    foro = breadboard(x, y, ncol=8, evid=[(3, "top"), (6, "bottom")])
    return foro


def cos_e_breadboard(x, y, w):
    mini_breadboard(x, y - 228)
    tx = x + 8 * SP + 60
    yy = titolo_sez(tx, y - 18, "Come funziona la breadboard")
    for s in ["I 5 fori di ogni colonna (a-e oppure f-j) sono collegati tra loro sotto la plastica: "
              "in verde due esempi.",
              "La scanalatura centrale separa la metà alta da quella bassa: la colonna 3 in alto "
              "NON è collegata alla colonna 3 in basso.",
              "Colonne diverse non sono collegate tra loro.",
              "I numeri delle colonne e le lettere delle righe sono stampati sulla breadboard: "
              "usali per trovare i fori indicati nel disegno."]:
        yy = wrap(tx, yy, "•  " + s, w - (tx - x), 9.6, 13.5) - 6
    return y - 240


# ------------------------------------------------------------------ parti comuni
CARICA = [
    ("Collega la UNO al telefono", "Pixel → hub USB-C → cavo blu → UNO. Sulla scheda si accende il LED verde ON."),
    ("Apri UNO Lab in Chrome e premi «Collega»", "Scegli la scheda nell'elenco e consenti l'accesso. In alto comparirà cosa c'è ora sulla scheda."),
]


def carica(nome):
    return CARICA + [("Premi «Carica sulla scheda» sul progetto " + nome,
                      "Aspetta la barra (pochi secondi): i LED TX e RX lampeggiano, è normale. "
                      "Alla fine si apre da sola la pagina dei comandi.")]


SICUREZZA = [
    "Fai e modifica i collegamenti solo con la UNO scollegata dal telefono.",
    "Controlla due volte i fili prima di dare corrente: un errore su 5V e GND può rovinare i componenti.",
    "Lavora su un tavolo, non su coperte o tessuti.",
]


def pagina_cosa_serve(y, cosa, info):
    x = 40
    for i, (k, v) in enumerate(info):
        bx = x + i * 172
        c.setFillColor(LIGHT); c.roundRect(bx, y - 34, 160, 40, 6, stroke=0, fill=1)
        text(bx + 10, y - 9, k, 8, "S", GREY); text(bx + 10, y - 25, v, 10.5, "SB")
    y -= 58
    y = titolo_sez(40, y, "Cosa ti serve")
    for s in cosa:
        y = wrap(48, y, "•  " + s, W - 96, 10, 14) - 1
    return y - 6


# ------------------------------------------------------------------ PROGETTI
def guida_blink():
    tot = 2
    header("LED integrato", "Il primo test: nessun filo, solo la scheda", 1, tot, 1)
    y = pagina_cosa_serve(H - 104, [
        "la scheda Elegoo UNO R3",
        "il cavo USB blu del kit (lato piatto A, lato quadrato B)",
        "il telefono con l'hub USB-C (o un adattatore OTG)",
    ], [("Difficoltà", "Facilissima"), ("Tempo", "5 minuti"), ("Fili da collegare", "Nessuno")])
    p = uno(130, 250, s=1.05, led_l=True)
    lx, ly = 130 + 112 * 1.05, 250 + 220 * 1.05 - 62 * 1.05
    c.setStrokeColor(ORANGE); c.setLineWidth(2.5); c.circle(lx, ly, 13, stroke=1, fill=0)
    c.setStrokeColor(ORANGE); c.setLineWidth(2)
    c.bezier(lx - 14, ly + 6, lx - 80, ly + 80, lx - 120, ly + 90, lx - 150, ly + 92)
    etichetta(lx - 150, ly + 92, "LED «L»: è questo che si accende", ORANGE, "c")
    text(W / 2, 215, "Il LED «L» è collegato internamente al pin 13: non serve nessun componente.", 9.5, "S", GREY, "c")
    riquadro(40, 190, W - 80, [
        "Questo progetto serve a verificare che tutto funzioni: telefono, hub, cavo, app e caricamento. "
        "Se qui va tutto bene, gli altri progetti differiscono solo per i collegamenti."],
        titolo="Perché iniziare da qui")
    c.showPage()

    header("LED integrato", "Passo passo", 2, tot, 1)
    y = titolo_sez(40, H - 110, "Passo passo")
    y = passi(40, y, W - 80, carica("«LED integrato»") + [
        ("Prova i comandi", "«Acceso» e «Spento» tengono il LED fisso; «Lampeggia» lo fa lampeggiare. "
         "Lo slider cambia la velocità: valori piccoli = lampeggio veloce."),
    ])
    y = titolo_sez(40, y - 6, "Cosa dovresti vedere")
    y = wrap(40, y, "Il LED arancione «L» vicino al pin 13 lampeggia circa due volte al secondo appena caricato il "
             "programma, e risponde subito ai pulsanti dell'app.", W - 80, 10, 14) - 14
    y = titolo_sez(40, y, "Se non funziona")
    y = problemi(y, [
        ("Il LED ON verde è spento", "La scheda non riceve corrente: controlla il cavo blu e l'hub; prova con un adattatore OTG senza hub."),
        ("«Collega» non trova la scheda", "Usa Chrome, ricollega il cavo e riprova. Se compare una richiesta di permesso USB, accettala."),
        ("Il caricamento si ferma con un errore", "Premi «Ricarica». Se ripete, premi il tasto rosso RESET sulla scheda appena premuto «Carica»."),
    ])
    riquadro(40, y - 4, W - 80, SICUREZZA, WARN_BG, WARN_FG, "Regole d'oro")
    c.showPage()


def problemi(y, lista):
    for a, b in lista:
        y = wrap(40, y, a, W - 80, 10.5, 14, "SB")
        y = wrap(40, y, b, W - 80, 9.4, 12.5, "S", GREY) - 6
    return y - 4


def disegno_servo(cx_servo=515, cy=380, ux=70, uy=270):
    pins = uno(ux, uy, hl={"D9": ORANGE, "5V": RED, "GND2": BROWN})
    # servo
    cx = cx_servo
    c.setFillColor(SERVO); c.roundRect(cx - 45, cy - 22, 90, 44, 4, stroke=0, fill=1)
    c.roundRect(cx - 60, cy - 6, 120, 12, 3, stroke=0, fill=1)
    c.setFillColor(white); c.circle(cx + 20, cy, 9, stroke=0, fill=1)
    c.roundRect(cx + 14, cy - 4, 48, 8, 4, stroke=0, fill=1)
    text(cx - 10, cy + 30, "Servo SG90", 10, "SB", black, "c")
    for yy, col in zip([cy + 6, cy, cy - 6], [ORANGE, RED, BROWN]):
        c.setStrokeColor(col); c.setLineWidth(3); c.line(cx - 45, yy, cx - 95, yy)
    c.setFillColor(HexColor("#222222")); c.rect(cx - 112, cy - 12, 18, 24, stroke=0, fill=1)
    sig, vcc, gnd = (cx - 112, cy + 6), (cx - 112, cy), (cx - 112, cy - 6)
    wire(sig, pins["D9"], ORANGE, (sig[0] - 5, uy + 300), (pins["D9"][0] + 10, uy + 300))
    wire(vcc, pins["5V"], RED, (vcc[0] + 5, uy - 70), (pins["5V"][0], uy - 65))
    wire(gnd, pins["GND2"], BROWN, (gnd[0] + 20, uy - 45), (pins["GND2"][0], uy - 45))
    etichetta(pins["D9"][0], uy + 286, "pin 9", ORANGE)
    etichetta(pins["5V"][0] - 22, uy - 30, "5V", RED)
    etichetta(pins["GND2"][0] + 26, uy - 18, "GND", BROWN)


def rotaie(x, y, n=18, sp=16):
    """Bordo della breadboard: riga + (rossa) e riga – (blu). Ritorna funzione foro(i, '+'|'-')."""
    w = n * sp + 40
    c.setFillColor(HexColor("#f6f6f3")); c.setStrokeColor(HexColor("#c8c8c0")); c.setLineWidth(1)
    c.roundRect(x, y, w, 46, 5, stroke=1, fill=1)
    def foro(i, r):
        return (x + 26 + i * sp, y + (32 if r == "+" else 14))
    c.setStrokeColor(RED); c.setLineWidth(1.2); c.line(x + 12, y + 41, x + w - 22, y + 41)
    c.setStrokeColor(ACC); c.line(x + 12, y + 5, x + w - 22, y + 5)
    for i in range(n):
        for r in "+-":
            fx, fy = foro(i, r)
            c.setFillColor(HexColor("#9a9a92")); c.rect(fx - 2, fy - 2, 4, 4, stroke=0, fill=1)
    text(x + w - 10, y + 28, "+", 11, "SB", RED, "c"); text(x + w - 10, y + 10, "–", 11, "SB", ACC, "c")
    text(x, y + 52, "bordo della breadboard: righe + e –", 8, "S", GREY)
    return foro


def hcsr04(x, y):
    """Sensore visto di fronte, piedini in basso. Ritorna i 4 piedini."""
    c.setFillColor(HexColor("#1f4fa8")); c.roundRect(x, y, 150, 62, 4, stroke=0, fill=1)
    for cx in (x + 33, x + 117):
        c.setFillColor(HexColor("#c9ccd1")); c.circle(cx, y + 36, 24, stroke=0, fill=1)
        c.setFillColor(HexColor("#3a3f47")); c.circle(cx, y + 36, 18, stroke=0, fill=1)
    text(x + 75, y + 50, "HC-SR04", 7, "SB", white, "c")
    nomi = ["Vcc", "Trig", "Echo", "Gnd"]
    pins = []
    for i, n in enumerate(nomi):
        px = x + 55 + i * 13
        c.saveState(); c.translate(px + 2.5, y + 8); c.rotate(90)
        c.setFont("S", 5.5); c.setFillColor(white); c.drawString(0, 0, n); c.restoreState()
        c.setStrokeColor(HexColor("#a0a0a0")); c.setLineWidth(1.8); c.line(px, y, px, y - 14)
        pins.append((px, y - 14))
    return dict(zip(nomi, pins))


def servo_disegno(cx, cy):
    c.setFillColor(SERVO); c.roundRect(cx - 45, cy - 22, 90, 44, 4, stroke=0, fill=1)
    c.roundRect(cx - 60, cy - 6, 120, 12, 3, stroke=0, fill=1)
    c.setFillColor(white); c.circle(cx + 20, cy, 9, stroke=0, fill=1)
    c.roundRect(cx + 14, cy - 4, 48, 8, 4, stroke=0, fill=1)
    text(cx, cy + 30, "Servo SG90", 10, "SB", black, "c")
    for yy, col in zip([cy + 6, cy, cy - 6], [ORANGE, RED, BROWN]):
        c.setStrokeColor(col); c.setLineWidth(3); c.line(cx - 45, yy, cx - 95, yy)
    c.setFillColor(HexColor("#222222")); c.rect(cx - 112, cy - 12, 18, 24, stroke=0, fill=1)
    return {"sig": (cx - 112, cy + 6), "vcc": (cx - 112, cy), "gnd": (cx - 112, cy - 6)}


PURPLE = HexColor("#7b3fc4")


def guida_servo():
    tot = 3
    header("Servo + sensore distanza", "Un motorino e un «occhio» a ultrasuoni: comando manuale, radar e segui-mano", 1, tot, 11)
    pagina_cosa_serve(H - 104, [
        "la UNO, il cavo USB blu e la breadboard (ne usi solo il bordo con le righe + e –)",
        "il servo SG90 e il sensore a ultrasuoni HC-SR04 (quello con i due «occhi»)",
        "4 cavetti maschio-femmina (per il sensore) e 5 maschio-maschio",
        "nastro biadesivo o un elastico, se vuoi montare il sensore sul servo per il radar",
    ], [("Difficoltà", "Media"), ("Tempo", "25 minuti"), ("Fili da collegare", "9")])
    r = rotaie(50, 440)
    sv = servo_disegno(495, 520)
    se = hcsr04(395, 330)
    p = uno(80, 70, hl={"D9": ORANGE, "D12": PURPLE, "D11": GREEN, "GNDT": BLK, "5V": RED}, s=0.88)
    wire(p["5V"], r(1, "+"), RED, (110, 15), (5, 140))
    wire(p["GNDT"], r(3, "-"), BLK, (p["GNDT"][0], 360), (r(3, "-")[0], 380))
    wire(sv["vcc"], r(15, "+"), RED, (sv["vcc"][0] - 40, 510), (r(15, "+")[0], 520))
    wire(sv["gnd"], r(16, "-"), BROWN, (sv["gnd"][0] - 20, 490), (r(16, "-")[0] + 10, 410))
    wire(sv["sig"], p["D9"], ORANGE, (300, 560), (p["D9"][0] - 30, 400))
    wire(se["Vcc"], r(9, "+"), RED, (se["Vcc"][0] - 20, 300), (r(9, "+")[0], 410))
    wire(se["Gnd"], r(11, "-"), BLK, (se["Gnd"][0] + 10, 280), (r(11, "-")[0] + 20, 390))
    wire(se["Trig"], p["D12"], PURPLE, (se["Trig"][0], 270), (p["D12"][0], 300))
    wire(se["Echo"], p["D11"], GREEN, (se["Echo"][0], 262), (p["D11"][0] + 10, 290))
    etichetta(p["5V"][0] + 30, 50, "5V", RED)
    etichetta(p["GNDT"][0] - 22, 276, "GND", BLK)
    etichetta(p["D9"][0] - 18, 262, "9", ORANGE)
    etichetta(p["D12"][0] - 4, 296, "12", PURPLE)
    etichetta(p["D11"][0] + 18, 276, "11", GREEN)
    c.showPage()

    header("Servo + sensore distanza", "Passo passo", 2, tot, 11)
    y = titolo_sez(40, H - 110, "Passo passo")
    y = passi(40, y, W - 80, [
        ("Alimenta il bordo della breadboard", "Un filo dal 5V della UNO (fila in basso) alla riga +, e uno dal GND accanto al 13 (fila in alto) alla riga –."),
        ("Servo", "Rosso → riga +, marrone → riga –, arancione → pin 9 della UNO."),
        ("Sensore HC-SR04 (cavetti maschio-femmina)", "Il lato femmina va sui piedini del sensore. Vcc → riga +, Gnd → riga –, Trig → pin 12, Echo → pin 11. I nomi sono stampati sotto i piedini."),
        ("Per il radar: monta il sensore sul servo", "Fissa il sensore sul braccio bianco del servo con biadesivo o elastico, con gli «occhi» rivolti in avanti. Lascia i fili morbidi così possono seguire la rotazione."),
    ] + carica("«Servo + sensore distanza»") + [
        ("Scegli la modalità in alto", "Manuale: slider e distanza in tempo reale. Radar: il servo gira da solo e il grafico mostra gli ostacoli come punti rossi. Segui: muovi la mano tra 5 e 40 cm dal sensore e il servo la segue."),
    ])
    y = titolo_sez(40, y - 4, "Se non funziona")
    problemi(y, [
        ("La distanza è sempre «fuori portata»", "Trig ed Echo potrebbero essere invertiti (12 e 11), oppure manca Vcc o Gnd. Il sensore misura da circa 2 cm a 4 m."),
        ("Il radar disegna punti strani", "Le superfici morbide (tende, divani) o molto inclinate riflettono male gli ultrasuoni: prova con un libro o una scatola davanti."),
        ("Il servo trema o la scheda si riavvia", "Il telefono non dà abbastanza corrente: usa lo schema di pagina 3."),
    ])
    c.showPage()

    header("Servo + sensore distanza", "Facoltativo: alimentazione dal modulo della breadboard", 3, tot, 11)
    y = wrap(40, H - 108, "Serve solo se il servo trema o se la UNO si riavvia mentre il servo si muove. "
             "Il servo prende la corrente dalla batteria 9V tramite il modulo di alimentazione, la UNO resta collegata al telefono.",
             W - 80, 10, 14)
    foro = breadboard(150, 410, ncol=18)
    # modulo alimentazione a sinistra
    bx, by = 150, 410
    c.setFillColor(BOARD); c.roundRect(bx - 95, by - 6, 90, 240, 5, stroke=0, fill=1)
    text(bx - 50, by + 120, "modulo", 9, "SB", white, "c"); text(bx - 50, by + 108, "alimentazione", 6.5, "SB", white, "c")
    for jy in (by + 200, by + 30):
        c.setFillColor(HexColor("#fff3c4")); c.rect(bx - 70, jy - 7, 40, 14, stroke=0, fill=1)
        text(bx - 50, jy - 3, "5V", 8, "SB", black, "c")
    text(bx - 50, by + 186, "ponticello", 7, "S", white, "c")
    # rotaie disegnate sopra
    c.setFillColor(HexColor("#fbe3e3")); c.rect(bx, by + 228, 18 * SP + 44, 14, stroke=0, fill=1)
    c.setFillColor(HexColor("#e1e9fb")); c.rect(bx, by + 242, 18 * SP + 44, 14, stroke=0, fill=1)
    text(bx + 18 * SP + 38, by + 231, "+", 10, "SB", RED, "r"); text(bx + 18 * SP + 38, by + 245, "–", 10, "SB", ACC, "r")
    c.setStrokeColor(RED); c.setLineWidth(1); c.line(bx + 6, by + 235, bx + 18 * SP + 26, by + 235)
    c.setStrokeColor(ACC); c.line(bx + 6, by + 249, bx + 18 * SP + 26, by + 249)
    text(bx - 50, by + 262, "rotaie: tutta la riga + è collegata, idem la riga –", 8, "S", GREY, "l")
    # batteria
    c.setFillColor(HexColor("#333333")); c.roundRect(40, 320, 55, 75, 6, stroke=0, fill=1)
    text(67, 353, "9V", 15, "SB", white, "c")
    c.setStrokeColor(black); c.setLineWidth(3); c.bezier(67, 395, 67, 440, 40, 460, 60, 500)
    c.setFillColor(HexColor("#111111")); c.rect(50, 495, 22, 30, stroke=0, fill=1)
    # servo
    cx, cy = 470, 290
    c.setFillColor(SERVO); c.roundRect(cx - 45, cy - 22, 90, 44, 4, stroke=0, fill=1)
    c.setFillColor(white); c.circle(cx + 20, cy, 9, stroke=0, fill=1)
    text(cx, cy + 30, "Servo", 10, "SB", black, "c")
    for yy, col in zip([cy + 6, cy, cy - 6], [ORANGE, RED, BROWN]):
        c.setStrokeColor(col); c.setLineWidth(3); c.line(cx - 45, yy, cx - 95, yy)
    c.setFillColor(HexColor("#222222")); c.rect(cx - 112, cy - 12, 18, 24, stroke=0, fill=1)
    p = uno(60, 110, hl={"D9": ORANGE, "GND2": BLK}, s=0.62)
    plus, minus = (bx + 30 + 12 * SP, by + 235), (bx + 30 + 14 * SP, by + 249)
    wire((cx - 112, cy), plus, RED, (330, 330), (plus[0], 380))
    wire((cx - 112, cy - 6), minus, BROWN, (360, 300), (minus[0] + 30, 420))
    wire((cx - 112, cy + 6), p["D9"], ORANGE, (300, 330), (p["D9"][0], 290))
    gm = (bx + 30 + 3 * SP, by + 249)
    wire(gm, p["GND2"], BLK, (gm[0] - 30, 300), (p["GND2"][0] - 40, 60))
    etichetta(gm[0] - 50, 330, "GND comune", BLK)
    y = 95
    riquadro(250, 225, W - 290, [
        "TOGLI il filo che va dal 5V della UNO alla riga +: ora la corrente arriva dal modulo.",
        "Rosso del servo e Vcc del sensore sulla riga +, marrone e Gnd sulla riga –.",
        "I ponticelli gialli del modulo su 5V, la batteria nella presa tonda.",
        "Un filo dalla riga – a un GND della UNO: obbligatorio.",
        "NON collegare il 5V del modulo al 5V della UNO.",
        "Inserisci il modulo rispettando + e – stampati sulla breadboard."], WARN_BG, WARN_FG, "Attenzione", 9)
    c.showPage()


def guida_rgb():
    tot = 2
    header("LED RGB", "Un LED che fa tutti i colori", 1, tot, 5)
    y = pagina_cosa_serve(H - 104, [
        "la UNO, il cavo USB blu e la breadboard",
        "il LED RGB (trasparente, con 4 piedini)",
        "3 resistenze da 220 Ω (fasce rosso-rosso-nero-nero-marrone)",
        "4 cavetti jumper maschio-maschio",
    ], [("Difficoltà", "Media"), ("Tempo", "20 minuti"), ("Fili da collegare", "4 + 3 resistenze")])
    foro = breadboard(150, 315)
    # LED: piedini in riga a, colonne 10-13
    legs = [foro(10, "a"), foro(11, "a"), foro(12, "a"), foro(13, "a")]
    cx = (legs[0][0] + legs[3][0]) / 2; cy = legs[0][1] + 42
    gambe(legs, cy - 10)
    c.setStrokeColor(HexColor("#9a9a9a")); c.setLineWidth(2.6); c.line(legs[1][0], cy - 10, legs[1][0], legs[1][1])
    c.setFillColor(HexColor("#f3f3f3")); c.setStrokeColor(HexColor("#b0b0b0")); c.setLineWidth(1)
    c.circle(cx, cy + 4, 20, stroke=1, fill=1)
    for i, (col, dx) in enumerate([("#ff5050", -7), ("#50d070", 3), ("#5080ff", 9)]):
        c.setFillColor(HexColor(col)); c.circle(cx + dx - 2, cy + 4 + (3 if i == 1 else -2), 4, stroke=0, fill=1)
    text(cx + 30, cy + 12, "LED RGB", 9.5, "SB")
    text(cx + 30, cy, "piedino lungo = GND", 8, "S", GREY)
    for (x, yy), lab, col in zip(legs, ["R", "–", "G", "B"], [RED, BLK, GREEN, BLUEW]):
        text(x - 6, yy + 14, lab, 7.5, "SB", col, "c")
    # resistenze da e a f
    for col in (10, 12, 13):
        resistenza(foro(col, "e"), foro(col, "f"), B220)
    p = uno(110, 58, hl={"D6": RED, "D5": GREEN, "D3": BLUEW, "GNDT": BLK}, s=0.82)
    wire(foro(10, "j"), p["D6"], RED, (foro(10, "j")[0], 270), (p["D6"][0] - 20, 290))
    wire(foro(12, "j"), p["D5"], GREEN, (foro(12, "j")[0], 280), (p["D5"][0], 300))
    wire(foro(13, "j"), p["D3"], BLUEW, (foro(13, "j")[0] + 20, 270), (p["D3"][0] + 10, 305))
    wire(foro(11, "d"), p["GNDT"], BLK, (foro(11, "d")[0] - 160, 390), (p["GNDT"][0], 300))
    etichetta(p["D6"][0] - 2, 256, "6", RED); etichetta(p["D5"][0] + 1, 272, "5", GREEN)
    etichetta(p["D3"][0] + 8, 256, "3", BLUEW); etichetta(p["GNDT"][0] - 14, 262, "GND", BLK)
    text(W / 2, 40, "Le resistenze scavalcano la scanalatura centrale: da riga e a riga f, nella stessa colonna.", 9, "S", GREY, "c")
    c.showPage()

    header("LED RGB", "Passo passo", 2, tot, 5)
    y = cos_e_breadboard(40, H - 92, W - 80)
    y = titolo_sez(40, y, "Riconoscere le resistenze da 220 Ω")
    resistenza_grande(48, y - 4, B220, "220 Ω", "rosso, rosso, nero, nero, marrone. Non hanno un verso.")
    y = titolo_sez(40, y - 34, "Passo passo")
    y = passi(40, y, W - 80, [
        ("LED RGB nella riga j, colonne 10-11-12-13",
         "Piedino più lungo in colonna 11. Il piedino singolo accanto (rosso) in 10, gli altri due (verde, blu) in 12 e 13."),
        ("Tre resistenze da 220 Ω, da f a e", "Nelle colonne 10, 12 e 13: ogni resistenza scavalca la scanalatura centrale."),
        ("Fili: a10 → pin 6, a12 → pin 5, a13 → pin 3", "I pin 6, 5, 3 sono nella fila in alto della UNO (scritti ~6, ~5, ~3)."),
        ("Filo: g11 → GND", "Il GND nella fila in alto, accanto al 13. Collega così il piedino lungo del LED."),
    ] + carica("«LED RGB»") + [
        ("Scegli un colore", "Con il quadratino colorato, gli slider Rosso-Verde-Blu o i campioni in basso."),
    ])
    y = titolo_sez(40, y - 4, "Se non funziona")
    problemi(y, [
        ("I colori sono scambiati", "Il LED è girato o spostato di una colonna: il piedino lungo deve essere in colonna 11."),
        ("Non si accende niente", "Controlla il filo da g11 a GND e che ogni resistenza sia nella colonna giusta. Mai collegare il LED senza resistenze."),
    ])
    c.showPage()


def guida_luce():
    tot = 2
    header("Sensore di luce", "Misura quanta luce c'è e la mostra in un grafico", 1, tot, 7)
    y = pagina_cosa_serve(H - 104, [
        "la UNO, il cavo USB blu e la breadboard",
        "la fotoresistenza (dischetto con una riga a zig-zag, 2 piedini)",
        "1 resistenza da 10 kΩ (fasce marrone-nero-nero-rosso-marrone)",
        "3 cavetti jumper maschio-maschio",
    ], [("Difficoltà", "Media"), ("Tempo", "15 minuti"), ("Fili da collegare", "3 + 1 resistenza")])
    p = uno(110, 415, hl={"5V": RED, "A0": YEL, "GND2": BLK}, s=0.82)
    foro = breadboard(150, 108)
    legs = [foro(6, "j"), foro(8, "j")]
    cx = (legs[0][0] + legs[1][0]) / 2; cy = legs[0][1] - 34
    gambe(legs, cy + 12)
    c.setFillColor(HexColor("#e8a05a")); c.circle(cx, cy, 14, stroke=0, fill=1)
    c.setStrokeColor(HexColor("#8a3b12")); c.setLineWidth(1.4)
    pth = c.beginPath(); pth.moveTo(cx - 9, cy + 5)
    for i in range(5): pth.lineTo(cx + 9 if i % 2 == 0 else cx - 9, cy + 5 - (i + 1) * 2.5)
    c.drawPath(pth, stroke=1, fill=0)
    text(cx + 22, cy - 3, "fotoresistenza (nessun verso)", 8.5, "S", GREY)
    resistenza(foro(8, "g"), foro(12, "g"), B10K)
    text(foro(10, "g")[0], foro(10, "g")[1] - 18, "10 kΩ", 8, "SB", GREY, "c")
    wire(foro(6, "f"), p["5V"], RED, (foro(6, "f")[0] - 20, 370), (p["5V"][0], 380))
    wire(foro(8, "f"), p["A0"], YEL, (foro(8, "f")[0] + 10, 380), (p["A0"][0], 360))
    wire(foro(12, "f"), p["GND2"], BLK, (foro(12, "f")[0] + 30, 395), (p["GND2"][0] + 10, 360))
    etichetta(p["5V"][0] - 22, 395, "5V", RED); etichetta(p["A0"][0] + 12, 395, "A0", YEL)
    etichetta(p["GND2"][0] + 4, 384, "GND", BLK)
    c.showPage()

    header("Sensore di luce", "Passo passo", 2, tot, 7)
    y = cos_e_breadboard(40, H - 92, W - 80)
    y = titolo_sez(40, y, "Riconoscere la resistenza da 10 kΩ")
    resistenza_grande(48, y - 4, B10K, "10 kΩ", "marrone, nero, nero, rosso, marrone. Non ha un verso.")
    y = titolo_sez(40, y - 34, "Passo passo")
    y = passi(40, y, W - 80, [
        ("Fotoresistenza nella riga a, colonne 6 e 8", "Non ha un verso: va bene in entrambi i sensi."),
        ("Resistenza 10 kΩ da d8 a d12", "Una gamba nella colonna 8 (insieme alla fotoresistenza), l'altra nella 12."),
        ("Fili: e6 → 5V, e8 → A0, e12 → GND", "Tutti e tre nella fila in basso della UNO: 5V e GND nel gruppo POWER, A0 nel gruppo ANALOG IN."),
    ] + carica("«Sensore di luce»") + [
        ("Guarda il grafico", "Copri la fotoresistenza con la mano: il valore scende. Avvicina la torcia del telefono: sale."),
    ])
    y = titolo_sez(40, y - 4, "Se non funziona")
    problemi(y, [
        ("Il valore resta a 0% o 100%", "Manca la resistenza da 10 kΩ, oppure è nella riga/colonna sbagliata."),
        ("Il valore non cambia con la mano", "Controlla il filo di A0: deve partire dalla colonna 8, la stessa della fotoresistenza e della resistenza."),
    ])
    c.showPage()


def guida_buzzer():
    tot = 2
    header("Buzzer", "Suona le note dal telefono", 1, tot, 4)
    y = pagina_cosa_serve(H - 104, [
        "la UNO, il cavo USB blu e la breadboard",
        "il buzzer PASSIVO (sotto si vede il circuito verde, senza adesivo sopra)",
        "2 cavetti jumper maschio-maschio",
    ], [("Difficoltà", "Facile"), ("Tempo", "10 minuti"), ("Fili da collegare", "2")])
    foro = breadboard(150, 305)
    legs = [foro(10, "a"), foro(13, "a")]
    cx = (legs[0][0] + legs[1][0]) / 2; cy = legs[0][1] + 48
    gambe(legs, cy - 20)
    c.setFillColor(HexColor("#1c1c1c")); c.circle(cx, cy, 26, stroke=0, fill=1)
    c.setFillColor(HexColor("#444444")); c.circle(cx, cy, 6, stroke=0, fill=1)
    text(legs[0][0] - 4, cy - 30, "+", 12, "SB", RED, "c")
    text(cx + 36, cy + 4, "buzzer passivo", 9.5, "SB"); text(cx + 36, cy - 8, "+ nella colonna 10", 8, "S", GREY)
    p = uno(110, 58, hl={"D8": ORANGE, "GNDT": BLK}, s=0.82)
    wire(foro(10, "e"), p["D8"], ORANGE, (foro(10, "e")[0], 260), (p["D8"][0] + 10, 300))
    wire(foro(13, "e"), p["GNDT"], BLK, (foro(13, "e")[0] + 60, 280), (p["GNDT"][0] - 30, 300))
    etichetta(p["D8"][0] + 4, 256, "8", ORANGE); etichetta(p["GNDT"][0] - 14, 262, "GND", BLK)
    text(W / 2, 40, "I fili partono dalla riga e: stessa colonna del piedino, quindi collegati al buzzer.", 9, "S", GREY, "c")
    c.showPage()

    header("Buzzer", "Passo passo", 2, tot, 4)
    y = cos_e_breadboard(40, H - 92, W - 80)
    y = riquadro(40, y, W - 80, [
        "Nel kit ci sono due buzzer quasi uguali. Il PASSIVO ha sotto il circuito verde in vista e niente adesivo. "
        "L'ATTIVO ha il fondo chiuso nero e spesso un adesivo sopra: suona sempre la stessa nota, qui non va bene."],
        titolo="Quale buzzer?")
    y = titolo_sez(40, y, "Passo passo")
    y = passi(40, y, W - 80, [
        ("Buzzer nella riga j, colonne 10 e 13", "Se c'è un «+» stampato, quel piedino va in colonna 10. Se i piedini sono più vicini usa la 10 e la 12, e sposta il filo di conseguenza."),
        ("Filo: f10 → pin 8", "Il pin 8 è nella fila in alto della UNO, a sinistra dello spazio vuoto."),
        ("Filo: f13 → GND", "Il GND nella fila in alto, accanto al 13."),
    ] + carica("«Buzzer»") + [
        ("Suona", "Tocca i tasti della tastiera. Puoi cambiare la durata delle note o provare una frequenza libera con lo slider."),
    ])
    y = titolo_sez(40, y - 4, "Se non funziona")
    problemi(y, [
        ("Suona sempre la stessa nota o solo «clic»", "Probabilmente stai usando il buzzer attivo: cambia buzzer."),
        ("Non suona niente", "Controlla che il filo del pin 8 parta dalla stessa colonna di un piedino del buzzer, e l'altro dalla colonna dell'altro piedino."),
    ])
    c.showPage()



# ======================================================================
# NUOVI PROGETTI
# ======================================================================
import math

VIOLA = HexColor("#7b3fc4"); AZZ = HexColor("#1f8fd1"); GRIGIO = HexColor("#777777")
ROSA = HexColor("#d63384"); VERDE_SC = HexColor("#1b7a3a")


def bb(x0, y0, ncol=20, sopra=True, sotto=True, inverti=False):
    """Breadboard con righe a-j e righe di alimentazione (+ esterna, – interna).
    foro(col, riga): riga in 'abcdefghij' oppure '+s','-s' (sopra) '+b','-b' (sotto)."""
    w, h = ncol * SP + 44, 11 * SP + 52
    top = y0 + h - 26

    def foro(col, r):
        x = x0 + 30 + (col - 1) * SP
        if r == "-s": return (x, y0 + h + 14)
        if r == "+s": return (x, y0 + h + 30)
        if r == "-b": return (x, y0 - 14)
        if r == "+b": return (x, y0 - 30)
        k = RIG.index(r)
        return (x, top - (k if k < 5 else k + 2) * SP)

    RIG = RIGHE
    c.setFillColor(HexColor("#f6f6f3")); c.setStrokeColor(HexColor("#c8c8c0")); c.setLineWidth(1)
    c.roundRect(x0, y0 - (40 if sotto else 0), w, h + (40 if sotto else 0) + (40 if sopra else 0), 6, stroke=1, fill=1)
    ce = (foro(1, RIG[4])[1] + foro(1, RIG[5])[1]) / 2
    c.setFillColor(HexColor("#e2e2dc")); c.rect(x0 + 6, ce - 5, w - 12, 10, stroke=0, fill=1)
    rails = (["-s", "+s"] if sopra else []) + (["-b", "+b"] if sotto else [])
    for r in rails:
        yy = foro(1, r)[1]
        col = RED if r[0] == "+" else ACC
        c.setStrokeColor(col); c.setLineWidth(1)
        off = 7 if (r in ("+s", "-b")) else -7
        c.line(x0 + 10, yy + off, x0 + w - 24, yy + off)
        text(x0 + w - 10, yy - 4, "+" if r[0] == "+" else "–", 11, "SB", col, "c")
        for i in range(1, ncol + 1):
            fx, fy = foro(i, r)
            c.setFillColor(HexColor("#9a9a92")); c.rect(fx - 2, fy - 2, 4, 4, stroke=0, fill=1)
    for col in range(1, ncol + 1):
        for r in RIG:
            fx, fy = foro(col, r)
            c.setFillColor(HexColor("#9a9a92")); c.rect(fx - 2, fy - 2, 4, 4, stroke=0, fill=1)
        fx, fy = foro(col, RIG[0]); text(fx, fy + 9, str(col), 6, "S", GREY, "c")
        fx, fy = foro(col, RIG[-1]); text(fx, fy - 15, str(col), 6, "S", GREY, "c")
    for r in RIG:
        fx, fy = foro(1, r); text(fx - 12, fy - 2.5, ETICHETTA_RIGA[r], 7, "S", GREY, "c")
    return foro


def ponticello(p0, p1, col=BLK):
    """Filo corto e diritto (es. verso una riga di alimentazione)."""
    wire(p0, p1, col, w=2.6)


def led_bb(foro, ca, colore, nome=None):
    """LED nella metà bassa: anodo (lungo) in colonna ca, catodo in ca+1, piedini in riga c."""
    pa, pk = foro(ca, "h"), foro(ca + 1, "h")
    cx, cy = (pa[0] + pk[0]) / 2, foro(ca, "f")[1] + 4
    c.setStrokeColor(HexColor("#9a9a9a")); c.setLineWidth(1.8)
    c.line(pa[0], cy, pa[0], pa[1]); c.line(pk[0], cy, pk[0], pk[1])
    c.setFillColor(HexColor("#9a9a9a")); c.circle(*pa, 2.2, stroke=0, fill=1); c.circle(*pk, 2.2, stroke=0, fill=1)
    c.setFillColor(HexColor(colore)); c.setStrokeColor(HexColor("#555555")); c.setLineWidth(0.6)
    c.circle(cx, cy, 10, stroke=1, fill=1)
    c.setFillColor(white); c.circle(cx - 3, cy + 3, 2.5, stroke=0, fill=1)
    text(pa[0] - 5, cy - 18, "+", 8, "SB", RED, "c")
    if nome: text(cx, cy + 14, nome, 7, "SB", GREY, "c")


def res_vert(foro, col, r_da="j", r_a="-b", bande=None):
    resistenza(foro(col, r_da), foro(col, r_a), bande or B220)


def pulsante_bb(foro, col):
    """Pulsante a cavallo della scanalatura: piedini in (col,e) (col+2,e) (col,f) (col+2,f)."""
    pts = [foro(col, "e"), foro(col + 2, "e"), foro(col, "f"), foro(col + 2, "f")]
    x0, x1 = pts[0][0] - 6, pts[1][0] + 6
    y0, y1 = pts[2][1] - 6, pts[0][1] + 6
    c.setFillColor(HexColor("#2b2b2b")); c.roundRect(x0, y0, x1 - x0, y1 - y0, 3, stroke=0, fill=1)
    c.setFillColor(HexColor("#555555")); c.circle((x0 + x1) / 2, (y0 + y1) / 2, 9, stroke=0, fill=1)
    for p in pts:
        c.setFillColor(HexColor("#bbbbbb")); c.circle(*p, 2.3, stroke=0, fill=1)


def due_piedini(foro, c1, c2, riga, disegna_corpo, etich=None):
    p1, p2 = foro(c1, riga), foro(c2, riga)
    cx, cy = (p1[0] + p2[0]) / 2, foro(c1, "f")[1] + 2
    c.setStrokeColor(HexColor("#9a9a9a")); c.setLineWidth(1.8)
    c.line(p1[0], cy, p1[0], p1[1]); c.line(p2[0], cy, p2[0], p2[1])
    c.setFillColor(HexColor("#9a9a9a")); c.circle(*p1, 2.2, stroke=0, fill=1); c.circle(*p2, 2.2, stroke=0, fill=1)
    disegna_corpo(cx, cy)
    if etich: text(cx, cy + 18, etich, 7, "SB", GREY, "c")


def corpo_tilt(cx, cy):
    c.setFillColor(HexColor("#1e1e1e")); c.roundRect(cx - 12, cy - 6, 24, 12, 5, stroke=0, fill=1)


def corpo_buzzer_attivo(cx, cy):
    c.setFillColor(HexColor("#1e1e1e")); c.circle(cx, cy, 13, stroke=0, fill=1)
    c.setFillColor(white); c.circle(cx, cy, 7, stroke=0, fill=1)
    text(cx, cy - 2.5, "+", 7, "SB", RED, "c")


def corpo_termistore(cx, cy):
    c.setFillColor(HexColor("#222222")); c.circle(cx, cy, 6, stroke=0, fill=1)


def potenziometro_bb(foro, col, riga="h"):
    """Potenziometro con piedini in col, col+2, col+4."""
    pts = [foro(col + 2 * i, riga) for i in range(3)]
    cx, cy = pts[1][0], foro(col, "f")[1] + 4
    c.setStrokeColor(HexColor("#9a9a9a")); c.setLineWidth(1.8)
    for p in pts: c.line(p[0], cy, p[0], p[1])
    c.setFillColor(HexColor("#2a5fb0")); c.roundRect(cx - 24, cy - 8, 48, 22, 3, stroke=0, fill=1)
    c.setFillColor(HexColor("#222222")); c.circle(cx, cy + 3, 9, stroke=0, fill=1)
    c.setFillColor(white); c.rect(cx - 1, cy + 3, 2, 8, stroke=0, fill=1)
    for p in pts: c.setFillColor(HexColor("#9a9a9a")); c.circle(*p, 2.2, stroke=0, fill=1)
    return pts


def chip_bb(foro, col, nome, nomi_pin=None):
    """Chip DIP16 a cavallo della scanalatura, tacca a sinistra. Ritorna pin(n) -> (colonna, metà)."""
    def pin(n):
        if n <= 8: return (col + n - 1, "f")
        return (col + 16 - n, "e")
    xa, xb = foro(col, "e")[0] - 7, foro(col + 7, "e")[0] + 7
    ya, yb = foro(col, "f")[1] - 2, foro(col, "e")[1] + 2
    c.setFillColor(HexColor("#1b1b1b")); c.rect(xa, ya, xb - xa, yb - ya, stroke=0, fill=1)
    c.setFillColor(HexColor("#555555")); c.circle(xa, (ya + yb) / 2, 5, stroke=0, fill=1)  # tacca
    text((xa + xb) / 2, (ya + yb) / 2 - 3, nome, 7.5, "SB", white, "c")
    for n in range(1, 17):
        cc, r = pin(n)
        fx, fy = foro(cc, r)
        c.setFillColor(HexColor("#c0c0c0")); c.rect(fx - 3, fy - 3, 6, 6, stroke=0, fill=1)
        lab = str(n)
        text(fx, fy + (-13 if r == "f" else 7), lab, 6, "SB", HexColor("#c03030"), "c")
    return pin


def wire_res(p0, p1, col, c1=None, c2=None, bande=None):
    """Filo con resistenza a metà percorso."""
    wire(p0, p1, col, c1, c2, w=2.4)
    if c1 is None:
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2; ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    else:
        t = 0.5
        bx = lambda a, b, cc, d: (1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t ** 2 * cc + t ** 3 * d
        mx, my = bx(p0[0], c1[0], c2[0], p1[0]), bx(p0[1], c1[1], c2[1], p1[1])
        ang = math.atan2(c2[1] - c1[1], c2[0] - c1[0])
    c.saveState(); c.translate(mx, my); c.rotate(math.degrees(ang))
    c.setFillColor(HexColor("#d9c49a")); c.roundRect(-12, -4.5, 24, 9, 4, stroke=0, fill=1)
    for i, cl in enumerate(bande or B220):
        c.setFillColor(HexColor(cl)); c.rect(-8 + i * 3.6, -4.5, 1.8, 9, stroke=0, fill=1)
    c.restoreState()


def modulo(x, y, w, hh, nome, pin_nomi, colore="#1f4fa8", sotto=True, nome_col=white):
    """Modulo generico con i piedini in basso (o in alto). Ritorna dict nome -> punto del piedino."""
    c.setFillColor(HexColor(colore)); c.roundRect(x, y, w, hh, 4, stroke=0, fill=1)
    text(x + w / 2, y + hh - 14, nome, 8, "SB", nome_col, "c")
    n = len(pin_nomi); step = 13
    x0 = x + w / 2 - (n - 1) * step / 2
    pins = {}
    for i, pn in enumerate(pin_nomi):
        px = x0 + i * step
        py = y if sotto else y + hh
        c.saveState(); c.translate(px + 2.5, (y + 6) if sotto else (y + hh - 6)); c.rotate(90)
        c.setFont("S", 5.5); c.setFillColor(nome_col)
        (c.drawString if sotto else c.drawRightString)(0, 0, pn); c.restoreState()
        c.setStrokeColor(HexColor("#a0a0a0")); c.setLineWidth(1.8)
        c.line(px, py, px, py - 12 if sotto else py + 12)
        pins[pn] = (px, py - 12 if sotto else py + 12)
    return pins


def modulo_alimentazione(foro, col_sx):
    """Modulo di alimentazione inserito a sinistra sulle righe + e – (sopra e sotto)."""
    xs = foro(col_sx, "a")[0] - 26
    ya, yb = foro(1, "+b")[1] - 10, foro(1, "+s")[1] + 10
    c.setFillColor(BOARD); c.roundRect(xs - 40, ya, 66, yb - ya, 5, stroke=0, fill=1)
    text(xs - 7, (ya + yb) / 2 + 6, "modulo", 7, "SB", white, "c")
    text(xs - 7, (ya + yb) / 2 - 4, "aliment.", 7, "SB", white, "c")
    for yy in (yb - 30, ya + 20):
        c.setFillColor(HexColor("#fff3c4")); c.rect(xs - 24, yy - 6, 34, 12, stroke=0, fill=1)
        text(xs - 7, yy - 3, "5V", 7, "SB", black, "c")
    c.setFillColor(HexColor("#111111")); c.rect(xs - 52, (ya + yb) / 2 - 22, 16, 30, stroke=0, fill=1)
    return (xs - 44, (ya + yb) / 2 - 22)


def batteria(x, y, presa):
    c.setFillColor(HexColor("#333333")); c.roundRect(x, y, 44, 62, 5, stroke=0, fill=1)
    text(x + 22, y + 26, "9V", 13, "SB", white, "c")
    c.setStrokeColor(black); c.setLineWidth(2.6)
    c.bezier(x + 22, y + 62, x + 22, y + 100, presa[0], presa[1] - 40, presa[0], presa[1])


def tabella(y, righe, w=W - 80, x=40):
    """righe: lista di (da, a, nota). Ritorna y finale."""
    c.setFillColor(HexColor("#e8ecf2")); c.rect(x, y - 4, w, 18, stroke=0, fill=1)
    text(x + 8, y + 1, "Da", 9, "SB"); text(x + w * 0.42, y + 1, "A", 9, "SB"); text(x + w * 0.70, y + 1, "Nota", 9, "SB")
    y -= 16
    for i, (a, b, n) in enumerate(righe):
        if i % 2: c.setFillColor(HexColor("#f6f8fb")); c.rect(x, y - 4, w, 15, stroke=0, fill=1)
        text(x + 8, y, a, 8.8); text(x + w * 0.42, y, b, 8.8, "SB"); text(x + w * 0.70, y, n, 8, "S", GREY)
        y -= 15
    return y - 10


class Flusso:
    """Impagina le sezioni della pagina 2 e va a capo con una nuova pagina se serve."""
    def __init__(self, titolo, num, pagina, tot):
        self.titolo, self.num, self.pag, self.tot = titolo, num, pagina, tot
        self.nuova()

    def nuova(self, cont=False):
        header(self.titolo, "Passo passo" + (" (continua)" if cont else ""), self.pag, self.tot, self.num)
        self.y = H - 110

    def spazio(self, serve):
        if self.y - serve < 50:
            c.showPage(); self.pag += 1; self.nuova(True)

    def sez(self, t):
        self.spazio(60); self.y = titolo_sez(40, self.y, t)

    def passi(self, lista, start=1):
        for i, (t, d) in enumerate(lista, start):
            n = len(simpleSplit(d or "", "S", 9.4, W - 110))
            self.spazio(20 + 12.5 * n)
            self.y = passi(40, self.y, W - 80, [(t, d)], i)

    def tabella(self, righe):
        self.spazio(20 + 15 * min(len(righe), 6))
        resto = list(righe)
        while resto:
            n = max(1, int((self.y - 70) // 15))
            self.y = tabella(self.y, resto[:n]); resto = resto[n:]
            if resto: c.showPage(); self.pag += 1; self.nuova(True)

    def problemi(self, lista):
        for a, b in lista:
            n = len(simpleSplit(b, "S", 9.4, W - 80))
            self.spazio(22 + 12.5 * n)
            self.y = problemi(self.y, [(a, b)]) + 4

    def nota(self, righe, titolo=None, bg=LIGHT, fg=black):
        n = sum(len(simpleSplit(r, "S", 9.8, W - 104)) for r in righe)
        self.spazio(40 + n * 14)
        self.y = riquadro(40, self.y, W - 80, righe, bg, fg, titolo)

    def fine(self):
        c.showPage()


# Conteggio pagine: generiamo due volte, la prima per contare
def guida_generica(titolo, sotto, num, cosa, info, disegna, passi_lista, righe_tab, probl, note=None, nota_finale=None):
    # pagina 1: disegno
    header(titolo, sotto, 1, guida_generica.tot, num)
    pagina_cosa_serve(H - 104, cosa, info)
    disegna()
    if nota_finale: text(W / 2, 28, nota_finale, 8.5, "S", GREY, "c")
    c.showPage()
    f = Flusso(titolo, num, 2, guida_generica.tot)
    if note: f.nota(note, "Prima di iniziare")
    f.sez("Passo passo")
    f.passi(passi_lista)
    f.sez("Tutti i collegamenti")
    f.tabella(righe_tab)
    f.sez("Se non funziona")
    f.problemi(probl)
    f.fine()
    return f.pag


guida_generica.tot = 2

RAIL_NOTE = ("Righe + e –: i fori lungo il bordo della breadboard sono collegati per tutta la lunghezza "
             "(su alcune breadboard la riga è interrotta a metà: se la linea rossa o blu ha una pausa, collega le due metà con un filo).")


def alim_uno(p, foro, colp=1, colm=2):
    """5V e GND della UNO verso le righe in basso."""
    wire(p["5V"], foro(colp, "+b"), RED, (p["5V"][0] - 40, p["5V"][1] - 40), (foro(colp, "+b")[0] - 60, foro(colp, "+b")[1] - 10))
    wire(p["GNDT"], foro(colm + 2, "-b"), BLK, (p["GNDT"][0], p["GNDT"][1] + 20), (foro(colm + 2, "-b")[0], foro(colm + 2, "-b")[1] - 20))


# ------------------------------------------------------------------ 2 SEMAFORO
def guida_semaforo():
    def dis():
        foro = bb(70, 300, 20, sopra=False)
        p = uno(85, 40, hl={"D12": RED, "D11": YEL, "D10": GREEN, "GNDT": BLK}, s=0.86)
        for ca, col, nome in [(4, "#e33b3b", "rosso"), (9, "#f2c230", "giallo"), (14, "#2fb35a", "verde")]:
            led_bb(foro, ca, col, nome)
            res_vert(foro, ca + 1)
        wire(foro(4, "j"), p["D12"], RED, (foro(4, "j")[0], 240), (p["D12"][0] - 30, 250))
        wire(foro(9, "j"), p["D11"], YEL, (foro(9, "j")[0], 240), (p["D11"][0] - 10, 250))
        wire(foro(14, "j"), p["D10"], GREEN, (foro(14, "j")[0], 240), (p["D10"][0] + 10, 250))
        wire(p["GNDT"], foro(2, "-b"), BLK, (p["GNDT"][0] - 10, 250), (foro(2, "-b")[0], 240))
        for k, (pin, col) in enumerate([("D12", RED), ("D11", YEL), ("D10", GREEN)]):
            etichetta(p[pin][0] + 14 * (k - 1), 202, pin[1:], col)
        etichetta(p["GNDT"][0] - 18, 206, "GND", BLK)
    return guida_generica("Semaforo", "Tre LED che si accendono come un semaforo vero", 2,
        ["la UNO, il cavo USB blu e la breadboard",
         "3 LED: uno rosso, uno giallo e uno verde",
         "3 resistenze da 220 Ω (rosso-rosso-nero-nero-marrone)",
         "4 cavetti maschio-maschio"],
        [("Difficoltà", "Facile"), ("Tempo", "15 minuti"), ("Fili da collegare", "4 + 3 resistenze")],
        dis,
        [("Riconosci il piedino lungo dei LED", "È il «+» (anodo). Nel disegno è a sinistra, segnato con +."),
         ("LED nella metà bassa, riga c", "Rosso: piedino lungo in colonna 4, corto in 5. Giallo: 9 e 10. Verde: 14 e 15."),
         ("Tre resistenze da 220 Ω", "Dalla colonna del piedino corto (riga a) alla riga – in basso: colonne 5, 10 e 15."),
         ("Fili verso la UNO", "Dalla riga a: colonna 4 → pin 12, colonna 9 → pin 11, colonna 14 → pin 10."),
         ("Filo di massa", "GND della UNO (fila in alto, accanto al 13) → riga – della breadboard."),
        ] + carica("«Semaforo»") + [
         ("Prova le modalità", "Automatico: il ciclo verde-giallo-rosso. Lampeggiante: giallo intermittente. Manuale: tocca le luci nell'app."),
        ],
        [("LED rosso, piedino lungo", "pin 12", "colonna 4"), ("LED giallo, piedino lungo", "pin 11", "colonna 9"),
         ("LED verde, piedino lungo", "pin 10", "colonna 14"), ("Piedini corti dei LED", "resistenza 220 Ω → riga –", "colonne 5, 10, 15"),
         ("GND della UNO", "riga – della breadboard", "")],
        [("Un LED non si accende", "Probabilmente è girato: scambia i due piedini. Il lungo va verso il pin della UNO."),
         ("Non si accende nessun LED", "Manca il filo dal GND della UNO alla riga –, oppure le resistenze non arrivano alla riga –."),
         ("Si accende il LED sbagliato", "Controlla quale colonna va a quale pin: 12 rosso, 11 giallo, 10 verde.")])


# ------------------------------------------------------------------ 3 PULSANTI
def guida_pulsanti():
    def dis():
        foro = bb(70, 250, 20)
        p = uno(85, 30, hl={"D2": ORANGE, "D3": VIOLA, "D4": GREEN, "GNDT": BLK}, s=0.80)
        pulsante_bb(foro, 3); pulsante_bb(foro, 9)
        text(foro(4, "e")[0], foro(4, "a")[1] + 18, "A", 9, "SB", ORANGE, "c")
        text(foro(10, "e")[0], foro(10, "a")[1] + 18, "B", 9, "SB", VIOLA, "c")
        due_piedini(foro, 15, 17, "h", corpo_tilt, "inclinazione")
        # massa dei pulsanti: diagonale in alto → riga – sopra
        ponticello(foro(5, "a"), foro(5, "-s")); ponticello(foro(11, "a"), foro(11, "-s"))
        ponticello(foro(17, "j"), foro(17, "-b"))
        # collega la riga – sopra con quella sotto
        wire(foro(19, "-s"), foro(19, "-b"), BLK, (foro(19, "-s")[0] + 40, foro(19, "-s")[1]), (foro(19, "-b")[0] + 40, foro(19, "-b")[1]), w=2.6)
        wire(foro(3, "j"), p["D2"], ORANGE, (foro(3, "j")[0], 190), (p["D2"][0] + 20, 220))
        wire(foro(9, "j"), p["D3"], VIOLA, (foro(9, "j")[0], 190), (p["D3"][0] + 10, 220))
        wire(foro(15, "j"), p["D4"], GREEN, (foro(15, "j")[0], 190), (p["D4"][0], 220))
        wire(p["GNDT"], foro(2, "-b"), BLK, (p["GNDT"][0] - 10, 200), (foro(2, "-b")[0], 190))
        etichetta(p["D2"][0] + 10, 176, "2", ORANGE); etichetta(p["D3"][0], 190, "3", VIOLA)
        etichetta(p["D4"][0] - 10, 176, "4", GREEN); etichetta(p["GNDT"][0] - 18, 182, "GND", BLK)
    return guida_generica("Pulsanti e inclinazione", "Leggere dei contatti: premuto o non premuto", 3,
        ["la UNO, il cavo USB blu e la breadboard",
         "2 pulsanti (quadratini neri con 4 piedini)",
         "il sensore di inclinazione (cilindretto nero con 2 piedini)",
         "8 cavetti maschio-maschio — non servono resistenze"],
        [("Difficoltà", "Facile"), ("Tempo", "15 minuti"), ("Fili da collegare", "8")],
        dis,
        [("Pulsanti a cavallo della scanalatura", "Pulsante A con i piedini nelle colonne 3 e 5 (righe e ed f), pulsante B nelle colonne 9 e 11. Spingili bene fino in fondo."),
         ("Massa dei pulsanti", "Dalla riga j, colonne 5 e 11 (piedino in diagonale rispetto a quello del pin), un filo corto alla riga – in alto."),
         ("Sensore di inclinazione", "Piedini in riga c, colonne 15 e 17. Colonna 17 (riga a) → riga – in basso. Non ha un verso."),
         ("Fili verso la UNO", "Dalla riga a: colonna 3 → pin 2, colonna 9 → pin 3, colonna 15 → pin 4."),
         ("Masse", "Collega la riga – in alto con quella in basso (filo a destra), e il GND della UNO alla riga – in basso."),
        ] + carica("«Pulsanti e inclinazione»") + [
         ("Premi e inclina", "Le spie nell'app si accendono quando premi. Il LED «L» della scheda si accende con il pulsante A."),
        ],
        [("Pulsante A (col. 3)", "pin 2", "riga a"), ("Pulsante A (col. 5)", "riga – in alto", "riga j, diagonale"),
         ("Pulsante B (col. 9)", "pin 3", "riga a"), ("Pulsante B (col. 11)", "riga – in alto", "riga j, diagonale"),
         ("Inclinazione (col. 15)", "pin 4", "riga a"), ("Inclinazione (col. 17)", "riga – in basso", "riga a"),
         ("Riga – in alto", "riga – in basso", "filo a destra"), ("GND della UNO", "riga – in basso", "")],
        [("Una spia resta sempre accesa", "Il pulsante è girato di 90°: usa sempre due piedini opposti in diagonale."),
         ("Una spia non si accende mai", "Il filo verso la riga – manca o è nella metà sbagliata della breadboard."),
         ("L'inclinazione cambia a caso", "È normale che la pallina dentro rimbalzi: inclina in modo deciso.")],
        note=["I pin della UNO hanno una resistenza interna di «pull-up»: quando il pulsante non è premuto il pin legge 5V, "
              "quando premi lo colleghi a GND. Per questo non servono resistenze."])


# ------------------------------------------------------------------ 6 POTENZIOMETRO
def guida_potenziometro():
    def dis():
        foro = bb(70, 300, 20, sopra=False)
        p = uno(85, 40, hl={"A0": ORANGE, "D9": RED, "GNDT": BLK, "5V": RED}, s=0.86)
        potenziometro_bb(foro, 4)
        ponticello(foro(4, "j"), foro(4, "+b"), RED); ponticello(foro(8, "j"), foro(8, "-b"), BLK)
        led_bb(foro, 13, "#e33b3b", "LED"); res_vert(foro, 14)
        wire(foro(6, "j"), p["A0"], ORANGE, (foro(6, "j")[0] - 70, 200), (p["A0"][0] + 80, 20))
        wire(foro(13, "j"), p["D9"], RED, (foro(13, "j")[0], 240), (p["D9"][0], 250))
        wire(p["GNDT"], foro(2, "-b"), BLK, (p["GNDT"][0] - 10, 250), (foro(2, "-b")[0], 240))
        wire(p["5V"], foro(1, "+b"), RED, (p["5V"][0] - 30, 0), (20, 200))
        etichetta(p["D9"][0] + 6, 202, "9", RED); etichetta(p["GNDT"][0] - 18, 206, "GND", BLK)
        etichetta(p["A0"][0] + 4, 22, "A0", ORANGE); etichetta(p["5V"][0] - 26, 22, "5V", RED)
    return guida_generica("Manopola (potenziometro)", "Una manopola che la UNO legge da 0 a 1023", 6,
        ["la UNO, il cavo USB blu e la breadboard",
         "il potenziometro da 10 kΩ (manopola con 3 piedini)",
         "1 LED rosso e 1 resistenza da 220 Ω",
         "6 cavetti maschio-maschio"],
        [("Difficoltà", "Facile"), ("Tempo", "15 minuti"), ("Fili da collegare", "6 + 1 resistenza")],
        dis,
        [("Potenziometro in riga c, colonne 4, 6 e 8", "Se i piedini sono più vicini, usa tre colonne di fila e sposta i fili di conseguenza."),
         ("Piedini esterni del potenziometro", "Colonna 4 (riga a) → riga + in basso; colonna 8 (riga a) → riga – in basso."),
         ("Piedino centrale → A0", "Dalla colonna 6, riga a, al pin A0 (fila in basso della UNO, gruppo ANALOG IN)."),
         ("LED", "Piedino lungo in colonna 13, corto in 14 (riga h). Resistenza 220 Ω dalla colonna 14 (riga j) alla riga –. Colonna 13 → pin 9."),
         ("Alimentazione", "5V della UNO → riga +, GND → riga –."),
        ] + carica("«Manopola»") + [
         ("Gira la manopola", "Il valore nell'app cambia da 0% a 100% e il LED si illumina di più o di meno. Con «Comanda l'app» regoli il LED dallo slider."),
        ],
        [("Potenziometro, esterno (col. 4)", "riga + in basso", ""), ("Potenziometro, centrale (col. 6)", "A0", ""),
         ("Potenziometro, esterno (col. 8)", "riga – in basso", ""), ("LED, piedino lungo (col. 13)", "pin 9", ""),
         ("LED, piedino corto (col. 14)", "resistenza 220 Ω → riga –", ""), ("5V della UNO", "riga +", ""), ("GND della UNO", "riga –", "")],
        [("Il valore va al contrario", "Normale: scambia i due fili dei piedini esterni se preferisci l'altro verso."),
         ("Il valore resta fermo", "Il filo di A0 deve partire dalla colonna del piedino centrale."),
         ("Il LED non cambia luminosità", "Deve essere collegato al pin 9 (ha il simbolo ~, che permette di variare la luce).")])


# ------------------------------------------------------------------ 8 METEO
def guida_meteo():
    def dis():
        foro = bb(40, 300, 16, sopra=False)
        p = uno(60, 40, hl={"D2": BLUEW, "A0": ORANGE, "GNDT": BLK, "5V": RED}, s=0.86)
        due_piedini(foro, 5, 7, "h", corpo_termistore, "termistore")
        ponticello(foro(5, "j"), foro(5, "+b"), RED)
        resistenza(foro(7, "i"), foro(11, "i"), B10K)
        text(foro(9, "i")[0], foro(9, "i")[1] + 9, "10 kΩ", 7, "SB", GREY, "c")
        ponticello(foro(11, "j"), foro(11, "-b"), BLK)
        dht = modulo(430, 400, 70, 90, "DHT11", ["S", "+", "–"], "#2b8ad8")
        c.setFillColor(HexColor("#e8f2fb"))
        for i in range(4):
            for j in range(5): c.rect(445 + j * 9, 430 + i * 9, 6, 6, stroke=0, fill=1)
        wire(dht["S"], p["D2"], BLUEW, (dht["S"][0], 300), (p["D2"][0] + 60, 260))
        wire(dht["+"], foro(14, "+b"), RED, (dht["+"][0], 330), (foro(14, "+b")[0] + 40, foro(14, "+b")[1] - 20))
        wire(dht["–"], foro(15, "-b"), BLK, (dht["–"][0] + 10, 320), (foro(15, "-b")[0] + 30, foro(15, "-b")[1] - 10))
        wire(foro(7, "j"), p["A0"], ORANGE, (foro(7, "j")[0] - 120, 220), (p["A0"][0] + 90, 20))
        wire(p["GNDT"], foro(2, "-b"), BLK, (p["GNDT"][0] - 10, 250), (foro(2, "-b")[0], 240))
        wire(p["5V"], foro(1, "+b"), RED, (p["5V"][0] - 30, 0), (10, 200))
        etichetta(p["D2"][0] + 12, 206, "2", BLUEW); etichetta(p["GNDT"][0] - 18, 206, "GND", BLK)
        etichetta(p["A0"][0] + 4, 22, "A0", ORANGE); etichetta(p["5V"][0] - 26, 22, "5V", RED)
    return guida_generica("Stazione meteo", "Temperatura e umidità con il DHT11, più un termistore", 8,
        ["la UNO, il cavo USB blu e la breadboard",
         "il modulo DHT11 (blu con la griglia, 3 piedini) e 3 cavetti maschio-femmina",
         "il termistore (piccola goccia nera con 2 piedini) e 1 resistenza da 10 kΩ",
         "5 cavetti maschio-maschio"],
        [("Difficoltà", "Media"), ("Tempo", "20 minuti"), ("Fili da collegare", "8 + 1 resistenza")],
        dis,
        [("Termistore in riga c, colonne 5 e 7", "Non ha un verso."),
         ("Resistenza 10 kΩ da b7 a b11", "Marrone-nero-nero-rosso-marrone. Poi colonna 11 (riga a) → riga – e colonna 5 (riga a) → riga +."),
         ("Colonna 7 → A0", "Il punto in mezzo tra termistore e resistenza va ad A0."),
         ("DHT11 con i cavetti maschio-femmina", "S → pin 2, piedino centrale (+) → riga +, – → riga –. Controlla le scritte sul modulo."),
         ("Alimentazione", "5V della UNO → riga +, GND → riga –."),
        ] + carica("«Stazione meteo»") + [
         ("Leggi le misure", "Ogni 2 secondi arrivano temperatura e umidità. Prova a soffiare sul DHT11: l'umidità sale. Stringi il termistore tra le dita: la sua temperatura sale."),
        ],
        [("DHT11 – S", "pin 2", "maschio-femmina"), ("DHT11 – + (centrale)", "riga +", "maschio-femmina"),
         ("DHT11 – –", "riga –", "maschio-femmina"), ("Termistore (col. 5)", "riga +", ""),
         ("Termistore (col. 7)", "A0", "punto di mezzo"), ("Resistenza 10 kΩ", "da i7 a i11", ""),
         ("Colonna 11", "riga –", ""), ("5V della UNO", "riga +", ""), ("GND della UNO", "riga –", "")],
        [("L'app scrive «errore» per il DHT11", "Controlla i 3 fili del modulo e che S vada proprio al pin 2. Alcuni moduli hanno l'ordine dei piedini diverso: guarda le scritte."),
         ("La temperatura del termistore è assurda", "Manca la resistenza da 10 kΩ, o è da 220 Ω: controlla le fasce."),
         ("Le due temperature sono un po' diverse", "È normale: sono sensori diversi, uno o due gradi di differenza ci stanno.")])


# ------------------------------------------------------------------ 9 JOYSTICK
def guida_joystick():
    def dis():
        p = uno(70, 120, hl={"A0": ORANGE, "A1": VIOLA, "D2": GREEN, "GNDT": BLK, "5V": RED}, s=1.0)
        js = modulo(380, 430, 110, 110, "Joystick", ["GND", "+5V", "VRx", "VRy", "SW"], "#1e1e1e")
        c.setFillColor(HexColor("#3a3a3a")); c.circle(435, 495, 26, stroke=0, fill=1)
        c.setFillColor(HexColor("#555555")); c.circle(435, 495, 14, stroke=0, fill=1)
        wire(js["GND"], p["GNDT"], BLK, (js["GND"][0], 380), (p["GNDT"][0], 400))
        wire(js["+5V"], p["5V"], RED, (js["+5V"][0] + 150, 300), (p["5V"][0] - 40, 40))
        wire(js["VRx"], p["A0"], ORANGE, (js["VRx"][0] + 130, 260), (p["A0"][0] + 30, 60))
        wire(js["VRy"], p["A1"], VIOLA, (js["VRy"][0] + 110, 250), (p["A1"][0] + 40, 70))
        wire(js["SW"], p["D2"], GREEN, (js["SW"][0], 390), (p["D2"][0] + 10, 400))
        etichetta(p["GNDT"][0] - 20, 370, "GND", BLK); etichetta(p["D2"][0] + 14, 370, "2", GREEN)
        etichetta(p["5V"][0] - 20, 112, "5V", RED); etichetta(p["A0"][0] - 6, 100, "A0", ORANGE); etichetta(p["A1"][0] + 20, 100, "A1", VIOLA)
    return guida_generica("Joystick", "Due potenziometri e un pulsante in un'unica levetta", 9,
        ["la UNO e il cavo USB blu",
         "il modulo joystick (nero, con la levetta e 5 piedini)",
         "5 cavetti maschio-femmina — niente breadboard"],
        [("Difficoltà", "Facile"), ("Tempo", "10 minuti"), ("Fili da collegare", "5")],
        dis,
        [("Leggi le scritte sui piedini del modulo", "GND, +5V, VRx, VRy, SW. Il lato femmina del cavetto va sul piedino del modulo."),
         ("GND → GND e +5V → 5V", "GND accanto al 13 nella fila in alto; 5V nella fila in basso."),
         ("VRx → A0 e VRy → A1", "Sono i due assi: orizzontale e verticale."),
         ("SW → pin 2", "È il pulsante che scatta premendo la levetta verso il basso."),
        ] + carica("«Joystick»") + [
         ("Muovi la levetta", "Il pallino blu segue i tuoi movimenti. Premi la levetta: il pallino diventa rosso e il contatore sale."),
        ],
        [("Joystick – GND", "GND", "fila in alto"), ("Joystick – +5V", "5V", "fila in basso"),
         ("Joystick – VRx", "A0", ""), ("Joystick – VRy", "A1", ""), ("Joystick – SW", "pin 2", "")],
        [("Il pallino va al contrario", "Dipende da come tieni il modulo: giralo, oppure scambia VRx e VRy."),
         ("Il pallino non si muove", "Controlla +5V e GND: senza alimentazione il modulo dà valori a caso o zero."),
         ("Il pulsante non scatta", "Premi la levetta in giù con decisione, finché senti il clic.")])


# ------------------------------------------------------------------ 10 ALLARME
def guida_allarme():
    def dis():
        foro = bb(70, 300, 20, sopra=False)
        p = uno(85, 40, hl={"D2": GREEN, "D8": ORANGE, "D12": RED, "GNDT": BLK}, s=0.86)
        due_piedini(foro, 3, 5, "h", corpo_tilt, "inclinazione")
        due_piedini(foro, 9, 11, "h", corpo_buzzer_attivo, "buzzer attivo")
        led_bb(foro, 15, "#e33b3b", "LED")
        ponticello(foro(5, "j"), foro(5, "-b")); ponticello(foro(11, "j"), foro(11, "-b")); res_vert(foro, 16)
        wire(foro(3, "j"), p["D2"], GREEN, (foro(3, "j")[0], 240), (p["D2"][0] + 20, 250))
        wire(foro(9, "j"), p["D8"], ORANGE, (foro(9, "j")[0], 240), (p["D8"][0], 250))
        wire(foro(15, "j"), p["D12"], RED, (foro(15, "j")[0], 240), (p["D12"][0] - 20, 250))
        wire(p["GNDT"], foro(2, "-b"), BLK, (p["GNDT"][0] - 10, 250), (foro(2, "-b")[0], 240))
        etichetta(p["D2"][0] + 8, 202, "2", GREEN); etichetta(p["D8"][0], 216, "8", ORANGE)
        etichetta(p["D12"][0] - 6, 202, "12", RED); etichetta(p["GNDT"][0] - 18, 206, "GND", BLK)
    return guida_generica("Allarme antifurto", "Se qualcuno muove la breadboard, scatta la sirena", 10,
        ["la UNO, il cavo USB blu e la breadboard",
         "il sensore di inclinazione e il buzzer ATTIVO (quello con l'adesivo sopra)",
         "1 LED rosso e 1 resistenza da 220 Ω",
         "6 cavetti maschio-maschio"],
        [("Difficoltà", "Media"), ("Tempo", "15 minuti"), ("Fili da collegare", "6 + 1 resistenza")],
        dis,
        [("Sensore di inclinazione in riga c, colonne 3 e 5", "Colonna 3 → pin 2, colonna 5 → riga –."),
         ("Buzzer ATTIVO in riga c, colonne 9 e 11", "Il piedino lungo (+, c'è un «+» anche sopra) in colonna 9 → pin 8. Colonna 11 → riga –. Lascia l'adesivo: smorza il suono."),
         ("LED rosso", "Lungo in 15, corto in 16. Resistenza 220 Ω dalla colonna 16 alla riga –. Colonna 15 → pin 12."),
         ("Massa", "GND della UNO → riga – della breadboard."),
        ] + carica("«Allarme antifurto»") + [
         ("Prova l'allarme", "Tieni ferma la breadboard e premi «Attiva»: il LED si accende fisso. Ora inclinala: scattano sirena e LED lampeggiante, e il telefono vibra. «Disattiva» spegne tutto."),
        ],
        [("Inclinazione (col. 3)", "pin 2", ""), ("Inclinazione (col. 5)", "riga –", ""),
         ("Buzzer attivo, + (col. 9)", "pin 8", "piedino lungo"), ("Buzzer attivo (col. 11)", "riga –", ""),
         ("LED, lungo (col. 15)", "pin 12", ""), ("LED, corto (col. 16)", "resistenza 220 Ω → riga –", ""),
         ("GND della UNO", "riga –", "")],
        [("Scatta appena lo attivo", "Il sensore è in bilico: posa la breadboard su un piano e aspetta un attimo prima di attivare."),
         ("La sirena fa un suono debole o un ronzio", "Stai usando il buzzer passivo: serve quello attivo, con l'adesivo."),
         ("Non scatta mai", "Inclina di più: la pallina dentro il sensore deve spostarsi. Controlla il filo del pin 2.")])


# ------------------------------------------------------------------ 12 TELECOMANDO
def disegno_telecomando(x, y):
    c.setFillColor(HexColor("#2b2f36")); c.roundRect(x, y, 70, 150, 14, stroke=0, fill=1)
    for i in range(7):
        for j in range(3):
            c.setFillColor(HexColor("#c23a3a") if (i, j) == (0, 0) else HexColor("#555b66"))
            c.circle(x + 15 + j * 20, y + 132 - i * 19, 7, stroke=0, fill=1)


def guida_telecomando():
    def dis():
        p = uno(70, 120, hl={"D11": ORANGE, "GNDT": BLK, "5V": RED}, s=1.0)
        ir = modulo(400, 450, 70, 70, "Ricevitore IR", ["G", "R", "Y"], "#1e1e1e")
        c.setFillColor(HexColor("#333333")); c.roundRect(420, 466, 30, 20, 8, stroke=0, fill=1)
        disegno_telecomando(495, 440)
        for k in range(3):
            c.setStrokeColor(HexColor("#d43c3c")); c.setLineWidth(1.2); c.setDash(3, 3)
            c.line(495, 520 - k * 8, 456, 505 - k * 4)
        c.setDash()
        wire(ir["G"], p["GNDT"], BLK, (ir["G"][0], 390), (p["GNDT"][0], 410))
        wire(ir["R"], p["5V"], RED, (ir["R"][0] + 160, 300), (p["5V"][0] - 40, 40))
        wire(ir["Y"], p["D11"], ORANGE, (ir["Y"][0], 380), (p["D11"][0], 420))
        etichetta(p["GNDT"][0] - 20, 370, "GND", BLK); etichetta(p["D11"][0] + 14, 370, "11", ORANGE)
        etichetta(p["5V"][0] - 20, 112, "5V", RED)
    return guida_generica("Telecomando a infrarossi", "La UNO riconosce i tasti del telecomando del kit", 12,
        ["la UNO e il cavo USB blu",
         "il modulo ricevitore a infrarossi (piccolo, nero, 3 piedini) e il telecomando",
         "3 cavetti maschio-femmina — niente breadboard",
         "la batteria a bottone del telecomando: togli la linguetta di plastica"],
        [("Difficoltà", "Facile"), ("Tempo", "10 minuti"), ("Fili da collegare", "3")],
        dis,
        [("Togli la linguetta dal telecomando", "È la striscia di plastica trasparente che sporge sotto: senza toglierla il telecomando non funziona."),
         ("Ricevitore: G → GND", "Su alcuni moduli è scritto «–»."),
         ("Ricevitore: R (centrale) → 5V", "Fila in basso della UNO."),
         ("Ricevitore: Y → pin 11", "Su alcuni moduli è scritto «S»: è il segnale."),
        ] + carica("«Telecomando»") + [
         ("Premi i tasti", "Punta il telecomando verso il ricevitore: il tasto premuto si illumina nell'app e il LED «L» della scheda lampeggia."),
        ],
        [("Ricevitore – G (o –)", "GND", "fila in alto"), ("Ricevitore – R (centrale)", "5V", "fila in basso"),
         ("Ricevitore – Y (o S)", "pin 11", "")],
        [("Non succede niente", "Hai tolto la linguetta del telecomando? Prova da vicino (30-50 cm), puntando bene il ricevitore."),
         ("Compare «sconosciuto»", "Il codice non è tra quelli del telecomando del kit (oppure era un disturbo): riprova."),
         ("Il LED del modulo non lampeggia", "Controlla G e R: senza alimentazione il ricevitore non funziona.")])


# ------------------------------------------------------------------ 13 REGISTRO
COL8 = ["#e33b3b"] * 8


def guida_registro():
    def dis():
        foro = bb(40, 290, 29)
        p = uno(70, 30, hl={"D12": AZZ, "D11": VIOLA, "D9": ORANGE, "GNDT": BLK, "5V": RED}, s=0.80)
        pin = chip_bb(foro, 3, "74HC595")
        def fp(n, r=None):
            cc, half = pin(n)
            return foro(cc, r or ("a" if half == "e" else "j"))
        # alimentazione del chip
        ponticello(fp(16), foro(pin(16)[0], "+s"), RED)
        ponticello(fp(10), foro(pin(10)[0], "+s"), RED)
        ponticello(fp(13), foro(pin(13)[0], "-s"), BLK)
        ponticello(fp(8), foro(pin(8)[0], "-b"), BLK)
        # LED
        for i in range(8):
            ca = 13 + 2 * i
            led_bb(foro, ca, "#e33b3b", f"Q{i}")
            res_vert(foro, ca + 1)
        # uscite → LED (filo dalla colonna del chip alla colonna dell'anodo, riga i)
        cols = [0, 1, 2, 3, 4, 5, 6, 7]
        for i in range(8):
            n = 15 if i == 0 else i
            ca = 13 + 2 * i
            if i == 0:
                a = fp(15, "b"); b = foro(ca, "i")
                wire(a, b, AZZ, (a[0] + 30, a[1] + 40), (b[0], b[1] + 60), w=2)
            else:
                a = fp(n, "i"); b = foro(ca, "i")
                wire(a, b, HexColor(["#1f8fd1", "#2a9d3a", "#d4a100", "#7b3fc4", "#d63384", "#f28c18", "#555555", "#1b7a3a"][i]),
                     (a[0], a[1] - 22 - i * 3), (b[0], b[1] - 22 - i * 3), w=2)
        # segnali
        wire(fp(14), p["D12"], AZZ, (fp(14)[0] - 60, fp(14)[1] + 10), (p["D12"][0] - 70, 230))
        wire(fp(12), p["D11"], VIOLA, (fp(12)[0] - 90, fp(12)[1] + 20), (p["D11"][0] - 60, 240))
        wire(fp(11), p["D9"], ORANGE, (fp(11)[0] - 110, fp(11)[1] + 30), (p["D9"][0] - 50, 250))
        # righe + e – : uniscile e collega la UNO
        wire(foro(29, "+s"), foro(29, "+b"), RED, (foro(29, "+s")[0] + 34, foro(29, "+s")[1]), (foro(29, "+b")[0] + 34, foro(29, "+b")[1]), w=2.4)
        wire(foro(28, "-s"), foro(28, "-b"), BLK, (foro(28, "-s")[0] + 24, foro(28, "-s")[1]), (foro(28, "-b")[0] + 24, foro(28, "-b")[1]), w=2.4)
        wire(p["GNDT"], foro(2, "-b"), BLK, (p["GNDT"][0] - 10, 240), (foro(2, "-b")[0], 230))
        wire(p["5V"], foro(1, "+b"), RED, (p["5V"][0] - 30, 0), (5, 200))
        etichetta(p["D12"][0] - 8, 192, "12", AZZ); etichetta(p["D11"][0] + 6, 200, "11", VIOLA)
        etichetta(p["D9"][0] + 12, 188, "9", ORANGE); etichetta(p["GNDT"][0] - 18, 196, "GND", BLK)
    return guida_generica("8 LED con il 74HC595", "Un chip che trasforma 3 pin in 8 uscite", 13,
        ["la UNO, il cavo USB blu e la breadboard",
         "il chip 74HC595 (16 piedini, scritta 74HC595)",
         "8 LED e 8 resistenze da 220 Ω",
         "circa 20 cavetti maschio-maschio"],
        [("Difficoltà", "Difficile"), ("Tempo", "40 minuti"), ("Fili da collegare", "~20 + 8 resistenze")],
        dis,
        [("Chip a cavallo della scanalatura, colonne 3-10", "La tacca (mezzaluna) a sinistra. Il piedino 1 è in basso a sinistra, si conta in senso antiorario: 1-8 in basso da sinistra, 9-16 in alto da destra. Spingi piano e dritto."),
         ("Alimentazione del chip", "Piedino 16 (col. 3, in alto) e piedino 10 (col. 9, in alto) → riga + in alto. Piedino 13 (col. 6, in alto) → riga – in alto. Piedino 8 (col. 10, in basso) → riga – in basso."),
         ("Unisci le righe", "Riga + in alto con riga + in basso, riga – in alto con riga – in basso (fili a destra). Poi 5V della UNO → riga + e GND → riga –."),
         ("8 LED in riga c", "LED Q0 con il lungo in colonna 13 e il corto in 14, Q1 in 15-16, e così via fino a Q7 in 27-28. Ogni corto → resistenza 220 Ω → riga – in basso."),
         ("Uscite del chip → LED", "Q0 è il piedino 15 (col. 4, in alto): filo dalla riga i al lungo del LED Q0. Q1-Q7 sono i piedini 1-7 (col. 3-9, in basso): fili dalla riga b al lungo dei LED Q1-Q7."),
         ("Segnali verso la UNO", "Piedino 14 (col. 5, in alto) → pin 12. Piedino 12 (col. 7, in alto) → pin 11. Piedino 11 (col. 8, in alto) → pin 9."),
        ] + carica("«8 LED con il 74HC595»") + [
         ("Gioca con le luci", "Tocca i LED nell'app per accenderli uno a uno, oppure scegli Supercar, Contatore, Casuale o Riempi."),
        ],
        [("74HC595 – 16 (VCC)", "riga + in alto", "col. 3"), ("74HC595 – 10 (MR)", "riga + in alto", "col. 9"),
         ("74HC595 – 13 (OE)", "riga – in alto", "col. 6"), ("74HC595 – 8 (GND)", "riga – in basso", "col. 10"),
         ("74HC595 – 14 (DS)", "pin 12", "col. 5"), ("74HC595 – 12 (latch)", "pin 11", "col. 7"),
         ("74HC595 – 11 (clock)", "pin 9", "col. 8"), ("74HC595 – 15 (Q0)", "LED Q0, piedino lungo", "col. 4 → 13"),
         ("74HC595 – 1…7 (Q1…Q7)", "LED Q1…Q7, piedino lungo", "col. 3…9 → 15…27"),
         ("Piedino corto di ogni LED", "resistenza 220 Ω → riga –", ""), ("Riga + in alto", "riga + in basso", ""),
         ("Riga – in alto", "riga – in basso", ""), ("5V della UNO", "riga +", ""), ("GND della UNO", "riga –", "")],
        [("Non si accende niente", "Controlla 16 e 10 su +, 8 e 13 su –, e che le righe in alto siano unite a quelle in basso."),
         ("I LED si accendono in ordine sbagliato", "Le uscite sono scambiate: Q0 è il piedino 15 (in alto), Q1 è il piedino 1 (in basso a sinistra)."),
         ("Il chip scalda", "Stacca subito: il chip è girato. La tacca deve essere a sinistra.")],
        note=["Il 74HC595 è un «registro a scorrimento»: la UNO gli manda 8 bit uno dopo l'altro su un solo filo (DS), "
              "scandendoli con il clock; con il latch li fa uscire tutti insieme sulle 8 uscite Q0-Q7.",
              "È il progetto con più fili finora: procedi con calma, una riga della tabella alla volta, e spunta ogni collegamento."])


# ------------------------------------------------------------------ 14 SETTE SEGMENTI
def dis_settesegmenti(ncol=24):
    foro = bb(40, 290, ncol)
    p = uno(70, 30, hl={"D12": AZZ, "D11": VIOLA, "D9": ORANGE, "GNDT": BLK, "5V": RED}, s=0.80)
    pin = chip_bb(foro, 3, "74HC595")
    def fp(n, r=None):
        cc, half = pin(n)
        return foro(cc, r or ("a" if half == "e" else "j"))
    ponticello(fp(16), foro(pin(16)[0], "+s"), RED); ponticello(fp(10), foro(pin(10)[0], "+s"), RED)
    ponticello(fp(13), foro(pin(13)[0], "-s"), BLK); ponticello(fp(8), foro(pin(8)[0], "-b"), BLK)
    # display: colonne 16-20, piedini in basso 1..5 (riga f), in alto 10..6 (riga e)
    xa, xb = foro(16, "e")[0] - 9, foro(20, "e")[0] + 9
    ya, yb = foro(16, "f")[1] - 4, foro(16, "e")[1] + 4
    c.setFillColor(HexColor("#2b2b2b")); c.rect(xa, ya - 14, xb - xa, yb - ya + 28, stroke=0, fill=1)
    cx, cy = (xa + xb) / 2, (ya + yb) / 2
    c.setFillColor(HexColor("#ff5a4a"))
    for (dx, dy, w_, h_) in [(-9, 16, 18, 3), (9, 2, 3, 14), (9, -16, 3, 14), (-9, -19, 18, 3), (-12, -16, 3, 14), (-12, 2, 3, 14), (-9, -1.5, 18, 3)]:
        c.rect(cx + dx, cy + dy, w_, h_, stroke=0, fill=1)
    c.circle(cx + 16, cy - 18, 2, stroke=0, fill=1)
    nomi_disp = {1: "e", 2: "d", 3: "–", 4: "c", 5: "dp", 6: "b", 7: "a", 8: "–", 9: "f", 10: "g"}
    def dpin(n):
        return (15 + n, "f") if n <= 5 else (16 + 10 - n, "e")
    for n in range(1, 11):
        cc, r = dpin(n); fx, fy = foro(cc, r)
        text(fx, fy + (-14 if r == "f" else 8), nomi_disp[n], 6.5, "SB", HexColor("#c03030"), "c")
    # comuni a massa
    ponticello(foro(18, "j"), foro(18, "-b")); ponticello(foro(18, "a"), foro(18, "-s"))
    # uscite chip -> resistenza -> segmento
    seg_q = {"a": 15, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "dp": 7}
    seg_pin = {"e": 1, "d": 2, "c": 4, "dp": 5, "b": 6, "a": 7, "f": 9, "g": 10}
    colori = {"a": "#1f8fd1", "b": "#2a9d3a", "c": "#d4a100", "d": "#7b3fc4", "e": "#d63384", "f": "#f28c18", "g": "#555555", "dp": "#1b7a3a"}
    for k, (s_, q) in enumerate(seg_q.items()):
        cc, half = pin(q)
        a = foro(cc, "c" if half == "e" else "h")
        dc, dr = dpin(seg_pin[s_])
        b = foro(dc, "c" if dr == "e" else "h")
        up = 1 if half == "e" else -1
        wire_res(a, b, HexColor(colori[s_]), (a[0], a[1] + up * (14 + k * 4)), (b[0], b[1] + (1 if dr == "e" else -1) * (14 + k * 4)))
    wire(fp(14), p["D12"], AZZ, (fp(14)[0] - 60, fp(14)[1] + 10), (p["D12"][0] - 70, 230))
    wire(fp(12), p["D11"], VIOLA, (fp(12)[0] - 90, fp(12)[1] + 20), (p["D11"][0] - 60, 240))
    wire(fp(11), p["D9"], ORANGE, (fp(11)[0] - 110, fp(11)[1] + 30), (p["D9"][0] - 50, 250))
    wire(foro(ncol, "+s"), foro(ncol, "+b"), RED, (foro(ncol, "+s")[0] + 34, foro(ncol, "+s")[1]), (foro(ncol, "+b")[0] + 34, foro(ncol, "+b")[1]), w=2.4)
    wire(foro(ncol - 1, "-s"), foro(ncol - 1, "-b"), BLK, (foro(ncol - 1, "-s")[0] + 24, foro(ncol - 1, "-s")[1]), (foro(ncol - 1, "-b")[0] + 24, foro(ncol - 1, "-b")[1]), w=2.4)
    wire(p["GNDT"], foro(2, "-b"), BLK, (p["GNDT"][0] - 10, 240), (foro(2, "-b")[0], 230))
    wire(p["5V"], foro(1, "+b"), RED, (p["5V"][0] - 30, 0), (5, 200))
    etichetta(p["D12"][0] - 8, 192, "12", AZZ); etichetta(p["D11"][0] + 6, 200, "11", VIOLA)
    etichetta(p["D9"][0] + 12, 188, "9", ORANGE); etichetta(p["GNDT"][0] - 18, 196, "GND", BLK)
    return foro, p


def guida_settesegmenti():
    dis = dis_settesegmenti
    return guida_generica("Display a 7 segmenti", "Una cifra luminosa, comandata dal 74HC595", 14,
        ["la UNO, il cavo USB blu e la breadboard",
         "il chip 74HC595 e il display a 7 segmenti da 1 cifra",
         "8 resistenze da 220 Ω",
         "circa 15 cavetti maschio-maschio"],
        [("Difficoltà", "Difficile"), ("Tempo", "40 minuti"), ("Fili da collegare", "~15 + 8 resistenze")],
        dis,
        [("Parti dal progetto 13", "Chip, alimentazione e i 3 fili verso la UNO sono identici al progetto «8 LED con il 74HC595»: se l'hai montato, togli solo LED e resistenze."),
         ("Display a cavallo della scanalatura, colonne 16-20", "Con il punto in basso a destra. I piedini centrali (colonna 18, in alto e in basso) sono il comune: entrambi → righe –."),
         ("8 resistenze da 220 Ω tra chip e display", "Ogni uscita del chip va a un segmento passando per una resistenza: Q0→a, Q1→b, Q2→c, Q3→d, Q4→e, Q5→f, Q6→g, Q7→punto. Usa una resistenza come «ponte» tra due colonne libere, poi due fili."),
         ("Dove sono i segmenti sul display", "In alto da sinistra: g, f, comune, a, b. In basso da sinistra: e, d, comune, c, punto."),
        ] + carica("«Display a 7 segmenti»") + [
         ("Prova", "Tocca una cifra, lancia il dado o fai partire il conto alla rovescia: il disegno nell'app mostra cosa dovrebbe accendersi."),
        ],
        [("Chip: 16, 10 / 13, 8", "riga + / riga –", "come progetto 13"), ("Chip: 14, 12, 11", "pin 12, 11, 9", "come progetto 13"),
         ("Q0 (15)", "220 Ω → segmento a", "display in alto, 4°"), ("Q1 (1)", "220 Ω → segmento b", "in alto, 5°"),
         ("Q2 (2)", "220 Ω → segmento c", "in basso, 4°"), ("Q3 (3)", "220 Ω → segmento d", "in basso, 2°"),
         ("Q4 (4)", "220 Ω → segmento e", "in basso, 1°"), ("Q5 (5)", "220 Ω → segmento f", "in alto, 2°"),
         ("Q6 (6)", "220 Ω → segmento g", "in alto, 1°"), ("Q7 (7)", "220 Ω → punto", "in basso, 5°"),
         ("Display: comuni (centrali)", "righe –", "in alto e in basso"), ("5V / GND della UNO", "riga + / riga –", "")],
        [("Le cifre escono «strane»", "Due segmenti sono scambiati: confronta con il disegno nell'app quale segmento manca o è in più."),
         ("Non si accende niente", "Il display potrebbe essere ad anodo comune: in quel caso i centrali vanno a + invece che a – (e le cifre appariranno invertite: scrivimi e adatto il programma)."),
         ("Un segmento è sempre spento", "Controlla la sua resistenza: deve collegare la colonna del chip con quella del segmento.")])


# ------------------------------------------------------------------ 15 LCD
NOMI_LCD = {1: "VSS", 2: "VDD", 3: "V0", 4: "RS", 5: "RW", 6: "E", 7: "D0", 8: "D1", 9: "D2", 10: "D3",
            11: "D4", 12: "D5", 13: "D6", 14: "D7", 15: "A", 16: "K"}


def col_lcd(n):
    """Colonna del piedino n: display con il piedino 16 (K) in colonna 12 e l'1 (VSS) in colonna 27."""
    return 28 - n


def dis_lcd(x0=28, ncol=31, pulsante=False):
    foro = bb(x0, 300, ncol, sopra=False, inverti=True)
    p = uno(70, 40, hl={"D7": AZZ, "D8": VIOLA, "D9": ORANGE, "D10": GREEN, "D11": ROSA, "D12": YEL, "GNDT": BLK, "5V": RED}, s=0.82)
    # display: piedini nella riga e (accanto alla scanalatura), corpo sopra la metà lontana, capovolto
    ye = foro(12, "f")[1]
    xa, xb = foro(12, "f")[0] - 150, foro(27, "f")[0] + 46
    xa = max(xa, x0 - 8)
    ya = ye + 8
    c.setFillColor(HexColor("#1f7a3a")); c.roundRect(xa, ya - 14, xb - xa, 150, 5, stroke=0, fill=1)
    c.setFillColor(HexColor("#1a1a1a")); c.rect(xa + 14, ya + 34, xb - xa - 28, 84, stroke=0, fill=1)
    c.setFillColor(HexColor("#3d7be0")); c.rect(xa + 24, ya + 44, xb - xa - 48, 64, stroke=0, fill=1)
    c.saveState(); c.translate((xa + xb) / 2, ya + 76); c.rotate(180)
    c.setFont("SB", 13); c.setFillColor(HexColor("#eaf2ff")); c.drawCentredString(0, -4, "UNO Lab")
    c.setFont("S", 8); c.drawCentredString(0, -18, "(capovolto, come nella foto)")
    c.restoreState()
    for n in range(1, 17):
        fx, fy = foro(col_lcd(n), "f")
        c.setFillColor(HexColor("#d4af37")); c.rect(fx - 3, fy - 3, 6, 12, stroke=0, fill=1)
        c.saveState(); c.translate(fx + 2.3, fy + 13); c.rotate(90)
        c.setFont("SB", 5.5); c.setFillColor(white); c.drawString(0, 0, NOMI_LCD[n]); c.restoreState()
    text(foro(27, "f")[0] + 8, ye + 12, "1", 6, "SB", white, "l")
    text(foro(12, "f")[0] - 8, ye + 12, "16", 6, "SB", white, "r")
    # potenziometro del contrasto: colonne 3-5-7, piedini in riga c
    legs = [foro(cc, "i") for cc in (3, 5, 7)]
    cy = foro(5, "h")[1] + 4
    c.setStrokeColor(HexColor("#9a9a9a")); c.setLineWidth(1.8)
    for q in legs: c.line(q[0], cy, q[0], q[1])
    c.setFillColor(HexColor("#2a5fb0")); c.roundRect(legs[1][0] - 24, cy - 8, 48, 20, 3, stroke=0, fill=1)
    c.setFillColor(HexColor("#222222")); c.circle(legs[1][0], cy + 2, 8, stroke=0, fill=1)
    text(legs[1][0], cy + 16, "contrasto", 6.5, "SB", GREY, "c")
    ponticello(foro(3, "j"), foro(3, "+b"), RED); ponticello(foro(7, "j"), foro(7, "-b"), BLK)
    wire(foro(5, "j"), foro(col_lcd(3), "i"), ORANGE, (foro(5, "j")[0] + 60, foro(5, "j")[1] - 2), (foro(col_lcd(3), "i")[0] - 60, foro(col_lcd(3), "i")[1] - 6), w=2.2)
    # alimentazione del display
    for n in (1, 5, 16):
        ponticello(foro(col_lcd(n), "j"), foro(col_lcd(n), "-b"), BLK)
    ponticello(foro(col_lcd(2), "j"), foro(col_lcd(2), "+b"), RED)
    res_vert(foro, col_lcd(15), "j", "+b")
    # segnali verso la UNO
    for n, pn, cl in [(4, "D7", AZZ), (6, "D8", VIOLA), (11, "D9", ORANGE), (12, "D10", GREEN), (13, "D11", ROSA), (14, "D12", YEL)]:
        a = foro(col_lcd(n), "g")
        wire(a, p[pn], cl, (a[0], 250), (p[pn][0], 255), w=2.4)
    wire(p["GNDT"], foro(1, "-b"), BLK, (p["GNDT"][0] - 30, 250), (foro(1, "-b")[0], 240))
    wire(p["5V"], foro(1, "+b"), RED, (p["5V"][0] - 30, 0), (5, 200))
    etichetta(p["GNDT"][0] - 18, 206, "GND", BLK)
    text(p["D7"][0] + 40, 196, "pin 7 · 8 · 9 · 10 · 11 · 12", 7.5, "SB", GREY, "c")
    return foro, p


PASSI_LCD = [
    ("Orienta la breadboard come nella foto", "Righe a-e verso di te (la e è quella accanto alla scanalatura centrale), righe + e – in basso."),
    ("Display con i piedini nella riga e, colonne 12-27", "Lo schermo resta sopra la metà lontana della breadboard, capovolto. Il piedino 16 (scritta K) va in colonna 12, l'1 (scritta VSS) in colonna 27: i nomi sono stampati sul display accanto ai piedini. I fili vanno nelle righe a-d della stessa colonna, dalla stessa parte della scanalatura."),
    ("Alimentazione del display", "VSS (col. 27), RW (col. 23) e K (col. 12) → riga –. VDD (col. 26) → riga +. A (col. 13) → resistenza 220 Ω → riga +."),
    ("Potenziometro del contrasto", "Piedini in riga b, colonne 3, 5, 7 (dalla riga a: colonna 3 → riga +, colonna 7 → riga –, colonna 5 → V0 in colonna 25)."),
    ("Segnali verso la UNO", "RS (col. 24) → pin 7; E (col. 22) → pin 8; D4 (col. 17) → pin 9; D5 (col. 16) → pin 10; D6 (col. 15) → pin 11; D7 (col. 14) → pin 12. D0-D3 (col. 18-21) restano liberi."),
    ("Alimentazione dalla UNO", "5V → riga +, GND → riga –."),
    ("Regola il contrasto", "Collega la UNO: se il display è acceso ma vuoto, gira lentamente il potenziometro finché compaiono le scritte (o dei rettangolini)."),
]

TAB_LCD = [("VSS (col. 27)", "riga –", "piedino 1"), ("VDD (col. 26)", "riga +", "piedino 2"), ("V0 (col. 25)", "centrale potenziometro", "piedino 3"),
           ("RS (col. 24)", "pin 7", "piedino 4"), ("RW (col. 23)", "riga –", "piedino 5"), ("E (col. 22)", "pin 8", "piedino 6"),
           ("D0-D3 (col. 21-18)", "liberi", "piedini 7-10"), ("D4 (col. 17)", "pin 9", "piedino 11"), ("D5 (col. 16)", "pin 10", "piedino 12"),
           ("D6 (col. 15)", "pin 11", "piedino 13"), ("D7 (col. 14)", "pin 12", "piedino 14"), ("A (col. 13)", "220 Ω → riga +", "retroilluminazione"),
           ("K (col. 12)", "riga –", "piedino 16"), ("Potenziometro, esterni", "riga + e riga –", "col. 3 e 7"),
           ("5V / GND della UNO", "riga + / riga –", "")]

def guida_lcd():
    dis = dis_lcd
    return guida_generica("Display LCD", "Scrivi testi dal telefono su un display da 16×2 caratteri", 15,
        ["la UNO, il cavo USB blu e la breadboard",
         "il display LCD 1602 (verde, 16 piedini già saldati)",
         "il potenziometro da 10 kΩ (per il contrasto) e 1 resistenza da 220 Ω",
         "circa 15 cavetti maschio-maschio"],
        [("Difficoltà", "Difficile"), ("Tempo", "40 minuti"), ("Fili da collegare", "~15 + 1 resistenza")],
        dis,
        PASSI_LCD[:-1] + [PASSI_LCD[-1]
    ] + carica("«Display LCD»") + [
         ("Scrivi", "Scrivi due righe nell'app e premi «Scrivi sul display», oppure «Mostra l'ora»."),
        ],
        TAB_LCD,
        [("Il display è acceso ma non scrive niente", "Gira il potenziometro del contrasto: è la causa più frequente."),
         ("Si vedono solo rettangoli pieni", "Il contrasto è giusto ma il display non riceve i dati: controlla RS (pin 7), E (pin 8) e D4-D7 (pin 9-12)."),
         ("Non si accende la luce", "Controlla pin 15 (con resistenza verso +) e pin 16 (verso –).")])


# ------------------------------------------------------------------ 16 VENTILATORE
def guida_ventilatore():
    def dis():
        foro = bb(110, 290, 20)
        p = uno(70, 30, hl={"D5": AZZ, "D3": VIOLA, "D4": GREEN, "GNDT": BLK}, s=0.80)
        presa = modulo_alimentazione(foro, 1)
        batteria(30, 300, presa)
        pin = chip_bb(foro, 8, "L293D")
        def fp(n, r=None):
            cc, half = pin(n)
            return foro(cc, r or ("a" if half == "e" else "j"))
        ponticello(fp(16), foro(pin(16)[0], "+s"), RED)
        ponticello(fp(13), foro(pin(13)[0], "-s"), BLK); ponticello(fp(12), foro(pin(12)[0], "-s"), BLK)
        ponticello(fp(4), foro(pin(4)[0], "-b"), BLK); ponticello(fp(5), foro(pin(5)[0], "-b"), BLK)
        ponticello(fp(8), foro(pin(8)[0], "+b"), RED)
        # motore
        mx, my = 470, 420
        c.setFillColor(HexColor("#c9ccd1")); c.roundRect(mx - 28, my - 18, 56, 36, 8, stroke=0, fill=1)
        c.setFillColor(HexColor("#f2c230")); c.roundRect(mx + 28, my - 6, 26, 12, 3, stroke=0, fill=1)
        text(mx, my - 3, "motore", 7.5, "SB", black, "c")
        c.setStrokeColor(HexColor("#888888")); c.setLineWidth(2)
        for a in (0, 120, 240):
            r = math.radians(a)
            c.line(mx + 60, my, mx + 60 + 28 * math.cos(r), my + 28 * math.sin(r))
        c.setFillColor(HexColor("#555555")); c.circle(mx + 60, my, 4, stroke=0, fill=1)
        wire((mx - 28, my + 6), fp(3, "i"), RED, (mx - 80, my + 20), (fp(3, "i")[0], fp(3, "i")[1] + 50), w=2.4)
        wire((mx - 28, my - 6), fp(6, "i"), BLK, (mx - 70, my - 30), (fp(6, "i")[0] + 10, fp(6, "i")[1] + 40), w=2.4)
        wire(fp(1), p["D5"], AZZ, (fp(1)[0], 220), (p["D5"][0] + 20, 240))
        wire(fp(2), p["D3"], VIOLA, (fp(2)[0], 215), (p["D3"][0] + 10, 245))
        wire(fp(7), p["D4"], GREEN, (fp(7)[0], 210), (p["D4"][0] - 10, 240))
        wire(p["GNDT"], foro(3, "-b"), BLK, (p["GNDT"][0] - 10, 240), (foro(3, "-b")[0], 230))
        etichetta(p["D5"][0] + 4, 186, "5", AZZ); etichetta(p["D3"][0] + 8, 200, "3", VIOLA)
        etichetta(p["D4"][0] - 6, 200, "4", GREEN); etichetta(p["GNDT"][0] - 18, 196, "GND", BLK)
    return guida_generica("Ventilatore", "Un motore vero, con il suo «driver» L293D", 16,
        ["la UNO, il cavo USB blu e la breadboard",
         "il chip L293D, il motorino 3-6V con l'elica",
         "il modulo di alimentazione e la batteria 9V con il suo cavetto",
         "circa 12 cavetti maschio-maschio"],
        [("Difficoltà", "Difficile"), ("Tempo", "35 minuti"), ("Fili da collegare", "~12")],
        dis,
        [("Modulo di alimentazione a sinistra", "Inseriscilo sulle righe + e – all'estremità sinistra della breadboard, rispettando + e –. I due ponticelli gialli su 5V. Batteria 9V nella presa tonda, ma interruttore spento."),
         ("L293D a cavallo della scanalatura, colonne 8-15", "Tacca a sinistra. Piedini 1-8 in basso da sinistra, 9-16 in alto da destra."),
         ("Alimentazione del chip", "16 → riga + in alto; 8 → riga + in basso; 4 e 5 → riga – in basso; 12 e 13 → riga – in alto."),
         ("Motore", "I due fili del motore vanno ai piedini 3 e 6 (colonne 10 e 13, in basso). Il verso non conta."),
         ("Segnali", "Piedino 1 (col. 8) → pin 5; piedino 2 (col. 9) → pin 3; piedino 7 (col. 14) → pin 4. GND della UNO → riga –."),
         ("Non collegare il 5V della UNO", "La corrente del motore arriva dal modulo con la batteria. La UNO resta collegata al telefono solo per i comandi."),
        ] + carica("«Ventilatore»") + [
         ("Accendi il modulo e prova", "Accendi l'interruttore del modulo (LED acceso). Muovi lo slider: a destra gira in un verso, a sinistra nell'altro. Tieni le dita lontane dall'elica."),
        ],
        [("Modulo alimentazione", "righe + e – (sinistra)", "ponticelli su 5V"), ("L293D – 1 (EN1)", "pin 5", "col. 8 in basso"),
         ("L293D – 2 (IN1)", "pin 3", "col. 9 in basso"), ("L293D – 3 (OUT1)", "motore, filo 1", "col. 10 in basso"),
         ("L293D – 4, 5 (GND)", "riga – in basso", "col. 11, 12"), ("L293D – 6 (OUT2)", "motore, filo 2", "col. 13 in basso"),
         ("L293D – 7 (IN2)", "pin 4", "col. 14 in basso"), ("L293D – 8 (VCC2)", "riga + in basso", "col. 15 in basso"),
         ("L293D – 12, 13 (GND)", "riga – in alto", "col. 12, 11 in alto"), ("L293D – 16 (VCC1)", "riga + in alto", "col. 8 in alto"),
         ("GND della UNO", "riga –", "massa comune")],
        [("Il motore non gira", "L'interruttore del modulo è acceso? La batteria è carica? Prova a velocità più alta: sotto il 20% può non partire."),
         ("Gira solo in un verso", "Controlla i fili dei piedini 2 (pin 3) e 7 (pin 4)."),
         ("La UNO si riavvia", "Manca il filo di massa comune, oppure il motore è alimentato dalla UNO invece che dal modulo.")],
        note=["I motori chiedono molta più corrente di quella che un pin della UNO può dare: il chip L293D fa da «interruttore potente», "
              "prendendo la corrente dalla batteria e lasciando alla UNO solo il compito di dare i comandi."])


# ------------------------------------------------------------------ 17 PASSO-PASSO
def guida_passo():
    def dis():
        r = rotaie(60, 470, n=14)
        p = uno(60, 80, hl={"D8": AZZ, "D9": VIOLA, "D10": GREEN, "D11": ORANGE, "GNDT": BLK}, s=0.86)
        # modulo alimentazione sulle rotaie (a sinistra)
        c.setFillColor(BOARD); c.roundRect(30, 455, 60, 76, 5, stroke=0, fill=1)
        text(60, 497, "modulo", 7, "SB", white, "c"); text(60, 487, "aliment.", 7, "SB", white, "c")
        c.setFillColor(HexColor("#fff3c4")); c.rect(44, 465, 32, 12, stroke=0, fill=1); text(60, 468, "5V", 7, "SB", black, "c")
        c.setFillColor(HexColor("#111111")); c.rect(18, 500, 14, 24, stroke=0, fill=1)
        batteria(10, 360, (25, 500))
        drv = modulo(380, 330, 120, 110, "ULN2003", ["IN1", "IN2", "IN3", "IN4", "–", "+"], "#2a9d3a")
        for i in range(4):
            c.setFillColor(HexColor("#ff5a4a")); c.circle(400 + i * 14, 410, 4, stroke=0, fill=1)
        c.setFillColor(white); c.rect(468, 392, 26, 32, stroke=0, fill=1)
        # motore
        c.setFillColor(HexColor("#c9ccd1")); c.circle(470, 540, 40, stroke=0, fill=1)
        c.setFillColor(HexColor("#2f6bd8")); c.roundRect(440, 500, 60, 20, 4, stroke=0, fill=1)
        c.setFillColor(HexColor("#f2c230")); c.circle(470, 552, 6, stroke=0, fill=1)
        text(470, 588, "28BYJ-48", 8, "SB", black, "c")
        c.setStrokeColor(HexColor("#d4a100")); c.setLineWidth(3); c.bezier(470, 500, 470, 470, 485, 450, 481, 424)
        wire(drv["IN1"], p["D8"], AZZ, (drv["IN1"][0], 280), (p["D8"][0] + 20, 320))
        wire(drv["IN2"], p["D9"], VIOLA, (drv["IN2"][0], 275), (p["D9"][0] + 10, 320))
        wire(drv["IN3"], p["D10"], GREEN, (drv["IN3"][0], 270), (p["D10"][0], 320))
        wire(drv["IN4"], p["D11"], ORANGE, (drv["IN4"][0], 265), (p["D11"][0] - 10, 320))
        wire(drv["+"], r(13, "+"), RED, (drv["+"][0] + 40, 300), (r(13, "+")[0] + 30, 450))
        wire(drv["–"], r(11, "-"), BLK, (drv["–"][0] + 20, 310), (r(11, "-")[0] + 20, 440))
        wire(p["GNDT"], r(3, "-"), BLK, (p["GNDT"][0] - 10, 320), (r(3, "-")[0], 420))
        etichetta(p["D8"][0] + 10, 280, "8", AZZ); etichetta(p["D9"][0] + 2, 292, "9", VIOLA)
        etichetta(p["D10"][0] - 6, 280, "10", GREEN); etichetta(p["D11"][0] - 14, 292, "11", ORANGE)
        etichetta(p["GNDT"][0] - 18, 286, "GND", BLK)
    return guida_generica("Motore passo-passo", "Un motore che si ferma esattamente dove vuoi", 17,
        ["la UNO, il cavo USB blu e la breadboard (solo il bordo con + e –)",
         "il motore 28BYJ-48 e il modulo driver ULN2003 (verde con 4 LED)",
         "il modulo di alimentazione e la batteria 9V",
         "6 cavetti maschio-femmina e 1 maschio-maschio"],
        [("Difficoltà", "Media"), ("Tempo", "25 minuti"), ("Fili da collegare", "7")],
        dis,
        [("Motore nel driver", "Il connettore bianco del motore entra nella presa bianca del driver solo in un verso: non forzare."),
         ("Modulo di alimentazione", "Inseriscilo sulle righe + e – a un'estremità della breadboard, ponticelli su 5V, batteria collegata ma interruttore spento."),
         ("Driver: + e –", "Con due cavetti maschio-femmina: + del driver → riga +, – del driver → riga –."),
         ("Driver: IN1-IN4", "Con 4 cavetti maschio-femmina: IN1 → pin 8, IN2 → pin 9, IN3 → pin 10, IN4 → pin 11."),
         ("Massa comune", "GND della UNO → riga –. Non collegare il 5V della UNO."),
        ] + carica("«Motore passo-passo»") + [
         ("Accendi il modulo e prova", "Tocca un punto del cerchio nell'app: il motore va a quell'angolo e i LED del driver lampeggiano. Prova anche «Giro intero» e la velocità."),
        ],
        [("Driver – IN1", "pin 8", "maschio-femmina"), ("Driver – IN2", "pin 9", "maschio-femmina"),
         ("Driver – IN3", "pin 10", "maschio-femmina"), ("Driver – IN4", "pin 11", "maschio-femmina"),
         ("Driver – +", "riga + (5V del modulo)", "maschio-femmina"), ("Driver – –", "riga –", "maschio-femmina"),
         ("GND della UNO", "riga –", "massa comune"), ("Motore", "presa bianca del driver", "")],
        [("Il motore vibra ma non gira", "L'ordine di IN1-IN4 è sbagliato: devono andare a 8, 9, 10, 11 nell'ordine."),
         ("Non succede niente", "Interruttore del modulo acceso? I LED del driver lampeggiano quando ricevono i comandi."),
         ("Il motore è lento", "È normale: ha un riduttore interno, al massimo fa circa 15 giri al minuto. In cambio è molto preciso.")],
        note=["Un motore passo-passo non gira liberamente: avanza a piccoli scatti («passi»). Questo, con il riduttore, fa 4096 mezzi passi per giro: "
              "la UNO li conta e sa sempre dove si trova l'albero."])




# ======================================================================
# LIVELLO 5 · PROGETTI AUTONOMI
# ======================================================================

BATTERIA = [
    "1. Carica il programma dall'app, con la UNO collegata al telefono.",
    "2. Stacca il cavo USB: il programma resta salvato nella scheda anche da spenta.",
    "3. Infila lo spinotto della batteria 9V nella presa tonda nera della UNO (quella vicino alla presa USB): il progetto parte da solo.",
    "4. Una batteria 9V dura qualche ora: staccala quando hai finito. Per modificare il progetto ricollega il telefono.",
]


def guida_autonoma(*args, **kw):
    """Come guida_generica, con in più la sezione «Usarlo a batteria»."""
    kw.setdefault("note", None)
    titolo, sotto, num, cosa, info, disegna, passi_lista, righe_tab, probl = args
    header(titolo, sotto, 1, guida_generica.tot, num)
    pagina_cosa_serve(H - 104, cosa, info)
    disegna()
    c.showPage()
    f = Flusso(titolo, num, 2, guida_generica.tot)
    if kw["note"]: f.nota(kw["note"], "Prima di iniziare")
    f.sez("Passo passo")
    f.passi(passi_lista)
    f.sez("Tutti i collegamenti")
    f.tabella(righe_tab)
    f.nota(BATTERIA, "🔋 Usarlo senza telefono, a batteria".replace("🔋 ", ""), HexColor("#eef7f1"), HexColor("#174d31"))
    f.sez("Se non funziona")
    f.problemi(probl)
    f.fine()
    return f.pag


def corpo_buzzer_passivo(cx, cy):
    c.setFillColor(HexColor("#1e1e1e")); c.circle(cx, cy, 13, stroke=0, fill=1)
    c.setFillColor(HexColor("#2f8f4a")); c.circle(cx, cy, 8, stroke=0, fill=1)
    c.setFillColor(HexColor("#1e1e1e")); c.circle(cx, cy, 3, stroke=0, fill=1)


def sr04_modulo(x, y):
    m = modulo(x, y, 130, 58, "HC-SR04", ["Vcc", "Trig", "Echo", "Gnd"], "#1f4fa8")
    for cx in (x + 28, x + 102):
        c.setFillColor(HexColor("#c9ccd1")); c.circle(cx, y + 32, 19, stroke=0, fill=1)
        c.setFillColor(HexColor("#3a3f47")); c.circle(cx, y + 32, 14, stroke=0, fill=1)
    return m


def piede_5v_gnd(p, foro, colp=1, colm=2, y5=0, xg=None):
    wire(p["GNDT"], foro(colm, "-b"), BLK, (p["GNDT"][0] - 10, 250), (foro(colm, "-b")[0], 240))
    wire(p["5V"], foro(colp, "+b"), RED, (p["5V"][0] - 30, y5), (5, 200))
    etichetta(p["GNDT"][0] - 18, 206, "GND", BLK); etichetta(p["5V"][0] - 26, 22, "5V", RED)


# ------------------------------------------------------------------ 18 PARCHEGGIO
def guida_parcheggio():
    def dis():
        foro = bb(60, 300, 20, sopra=False)
        p = uno(75, 40, hl={"D5": GREEN, "D6": YEL, "D7": RED, "D8": VIOLA, "D12": AZZ, "D11": ORANGE, "GNDT": BLK, "5V": RED}, s=0.86)
        for ca, col, nome in [(3, "#2fb35a", "verde"), (7, "#f2c230", "giallo"), (11, "#e33b3b", "rosso")]:
            led_bb(foro, ca, col, nome); res_vert(foro, ca + 1)
        due_piedini(foro, 15, 17, "h", corpo_buzzer_passivo, "buzzer passivo")
        ponticello(foro(17, "j"), foro(17, "-b"))
        wire(foro(3, "j"), p["D5"], GREEN, (foro(3, "j")[0], 240), (p["D5"][0] - 40, 260), w=2.6)
        wire(foro(7, "j"), p["D6"], YEL, (foro(7, "j")[0], 240), (p["D6"][0] - 20, 260), w=2.6)
        wire(foro(11, "j"), p["D7"], RED, (foro(11, "j")[0], 240), (p["D7"][0], 260), w=2.6)
        wire(foro(15, "j"), p["D8"], VIOLA, (foro(15, "j")[0], 240), (p["D8"][0], 260), w=2.6)
        s = sr04_modulo(415, 150)
        wire(s["Trig"], p["D12"], AZZ, (s["Trig"][0], 100), (p["D12"][0] + 10, 280))
        wire(s["Echo"], p["D11"], ORANGE, (s["Echo"][0], 90), (p["D11"][0] + 20, 290))
        wire(s["Vcc"], foro(19, "+b"), RED, (s["Vcc"][0] - 20, 110), (foro(19, "+b")[0] + 10, foro(19, "+b")[1] - 40))
        wire(s["Gnd"], foro(20, "-b"), BLK, (s["Gnd"][0] + 20, 120), (foro(20, "-b")[0] + 30, foro(20, "-b")[1] - 30))
        piede_5v_gnd(p, foro)
        text(p["D7"][0], 196, "pin 5 · 6 · 7 · 8 · 11 · 12", 7.5, "SB", GREY, "c")
    return guida_autonoma("Sensore di parcheggio", "Bip sempre più veloci quando ti avvicini, come in auto", 18,
        ["la UNO, il cavo USB blu, la breadboard e la batteria 9V con spinotto",
         "il sensore a ultrasuoni HC-SR04 e 4 cavetti maschio-femmina",
         "3 LED (verde, giallo, rosso), 3 resistenze da 220 Ω e il buzzer PASSIVO",
         "7 cavetti maschio-maschio"],
        [("Difficoltà", "Media"), ("Tempo", "30 minuti"), ("Fili da collegare", "11 + 3 resistenze")],
        dis,
        [("LED nella riga c", "Verde: lungo in colonna 3, corto in 4. Giallo: 7-8. Rosso: 11-12. Ogni corto → resistenza 220 Ω → riga – in basso."),
         ("Buzzer passivo in riga c, colonne 15 e 17", "Quello senza adesivo, con il circuito verde sotto. + in colonna 15. Colonna 17 → riga –."),
         ("Fili verso la UNO", "Colonna 3 → pin 5, colonna 7 → pin 6, colonna 11 → pin 7, colonna 15 → pin 8."),
         ("Sensore HC-SR04 (maschio-femmina)", "Vcc → riga +, Gnd → riga –, Trig → pin 12, Echo → pin 11."),
         ("Alimentazione", "5V della UNO → riga +, GND → riga –."),
        ] + carica("«Sensore di parcheggio»") + [
         ("Prova", "Avvicina la mano al sensore: verde oltre 50 cm, giallo con bip lenti, rosso con bip veloci, suono continuo sotto gli 8 cm."),
        ],
        [("LED verde, lungo (col. 3)", "pin 5", ""), ("LED giallo, lungo (col. 7)", "pin 6", ""), ("LED rosso, lungo (col. 11)", "pin 7", ""),
         ("Piedini corti dei LED", "220 Ω → riga –", "col. 4, 8, 12"), ("Buzzer passivo + (col. 15)", "pin 8", ""),
         ("Buzzer passivo (col. 17)", "riga –", ""), ("HC-SR04 – Vcc / Gnd", "riga + / riga –", "maschio-femmina"),
         ("HC-SR04 – Trig / Echo", "pin 12 / pin 11", "maschio-femmina"), ("5V / GND della UNO", "riga + / riga –", "")],
        [("Resta sempre verde", "Il sensore non misura: controlla Trig (12) ed Echo (11) e l'alimentazione del sensore."),
         ("Il bip è un ronzio sordo", "Stai usando il buzzer attivo: serve quello passivo, che sa fare note diverse."),
         ("Misure che saltano", "Gli ultrasuoni rimbalzano male su stoffa e superfici inclinate: prova con una scatola o un libro.")])


# ------------------------------------------------------------------ 19 TERMOMETRO
def guida_termometro():
    def dis():
        foro, p = dis_lcd()
        dht = modulo(420, 70, 70, 90, "DHT11", ["S", "+", "–"], "#2b8ad8")
        c.setFillColor(HexColor("#e8f2fb"))
        for i in range(4):
            for j in range(5): c.rect(435 + j * 9, 100 + i * 9, 6, 6, stroke=0, fill=1)
        wire(dht["S"], p["D2"], BLUEW, (dht["S"][0], 40), (p["D2"][0] + 40, 270), w=2.6)
        wire(dht["+"], foro(27, "+b"), RED, (dht["+"][0] + 10, 210), (foro(27, "+b")[0], foro(27, "+b")[1] - 30), w=2.6)
        wire(dht["–"], foro(28, "-b"), BLK, (dht["–"][0] + 30, 220), (foro(28, "-b")[0] + 10, foro(28, "-b")[1] - 30), w=2.6)
        etichetta(p["D2"][0] + 16, 190, "2", BLUEW)
    return guida_autonoma("Termometro con LCD", "Temperatura e umidità sempre in vista, anche a batteria", 19,
        ["tutto il montaggio del progetto 15 «Display LCD» (display, potenziometro, resistenza 220 Ω)",
         "il modulo DHT11 e 3 cavetti maschio-femmina",
         "la batteria 9V con spinotto"],
        [("Difficoltà", "Difficile"), ("Tempo", "45 minuti"), ("Fili da collegare", "~18")],
        dis,
        [("Monta il display come nel progetto 15", "Display nella riga e, colonne 12-27 (VSS a destra in colonna 27), potenziometro del contrasto nelle colonne 3-5-7. Se l'hai già montato, servono solo 3 fili in più."),
         ("DHT11: S → pin 2", "Il pin 2 è nella fila in alto della UNO, a destra."),
         ("DHT11: + → riga +, – → riga –", "Con cavetti maschio-femmina: il lato femmina sul modulo."),
        ] + carica("«Termometro con LCD»") + [
         ("Leggi il display", "Riga 1: temperatura e umidità. Riga 2: minima e massima da quando è acceso. Se non vedi niente gira il potenziometro del contrasto."),
        ],
        [("Display LCD", "come progetto 15", "pin 7-12"), ("DHT11 – S", "pin 2", "maschio-femmina"),
         ("DHT11 – +", "riga +", "maschio-femmina"), ("DHT11 – –", "riga –", "maschio-femmina")],
        [("Il display è acceso ma vuoto anche girando il contrasto", "I fili devono stare dalla stessa parte della scanalatura dei piedini del display (righe a-d), nella stessa colonna."),
         ("Il display scrive «Sensore assente»", "Controlla i 3 fili del DHT11 e le scritte sul modulo: S deve andare al pin 2."),
         ("Il display è vuoto", "Gira il potenziometro del contrasto."),
         ("La minima e la massima sono strane", "Si azzerano a ogni accensione; puoi azzerarle anche dall'app.")])


# ------------------------------------------------------------------ 20 SIMON
def guida_simon():
    def dis():
        foro = bb(30, 250, 29)
        p = uno(70, 30, hl={"D2": RED, "D3": GREEN, "D4": BLUEW, "D5": YEL, "D6": RED, "D7": GREEN, "D8": BLUEW, "D9": YEL, "D10": VIOLA, "GNDT": BLK}, s=0.80)
        colori = [("#e33b3b", RED, "rosso"), ("#2fb35a", GREEN, "verde"), ("#3b7be3", BLUEW, "blu"), ("#f2c230", YEL, "giallo")]
        for i, (hexc, col, nome) in enumerate(colori):
            cb = 2 + 4 * i
            pulsante_bb(foro, cb)
            text(foro(cb + 1, "a")[0], foro(cb + 1, "a")[1] + 18, nome, 7, "SB", col, "c")
            ponticello(foro(cb + 2, "a"), foro(cb + 2, "-s"))
            ca = 19 + 2 * i
            led_bb(foro, ca, hexc)
            res_vert(foro, ca + 1)
            wire(foro(cb, "j"), p[f"D{6 + i}"], col, (foro(cb, "j")[0], 200), (p[f"D{6 + i}"][0], 230), w=2.4)
            wire(foro(ca, "j"), p[f"D{2 + i}"], col, (foro(ca, "j")[0], 205), (p[f"D{2 + i}"][0] + 10, 225), w=2.4)
        due_piedini(foro, 27, 29, "h", corpo_buzzer_passivo, "buzzer")
        ponticello(foro(29, "j"), foro(29, "-b"))
        wire(foro(27, "j"), p["D10"], VIOLA, (foro(27, "j")[0], 210), (p["D10"][0] + 20, 230), w=2.4)
        wire(foro(29, "-s"), foro(29, "-b"), BLK, (foro(29, "-s")[0] + 34, foro(29, "-s")[1]), (foro(29, "-b")[0] + 34, foro(29, "-b")[1]), w=2.4)
        wire(p["GNDT"], foro(1, "-b"), BLK, (p["GNDT"][0] - 20, 240), (foro(1, "-b")[0], 230))
        etichetta(p["GNDT"][0] - 18, 190, "GND", BLK)
        text(p["D7"][0] + 10, 184, "pin 2 … 10", 8, "SB", GREY, "c")
    return guida_autonoma("Gioco Simon", "Il gioco della memoria con luci, suoni e pulsanti", 20,
        ["la UNO, il cavo USB blu, la breadboard e la batteria 9V con spinotto",
         "4 LED (rosso, verde, blu, giallo) e 4 resistenze da 220 Ω",
         "4 pulsanti e il buzzer PASSIVO",
         "circa 16 cavetti maschio-maschio"],
        [("Difficoltà", "Difficile"), ("Tempo", "45 minuti"), ("Fili da collegare", "~16 + 4 resistenze")],
        dis,
        [("4 pulsanti a cavallo della scanalatura", "Nelle colonne 2-4 (rosso), 6-8 (verde), 10-12 (blu), 14-16 (giallo). Metti accanto un pezzetto di carta colorata o ricordati l'ordine."),
         ("Massa dei pulsanti", "Dalla riga j delle colonne 4, 8, 12, 16 (piedino in diagonale) un filo corto alla riga – in alto."),
         ("Pulsanti → UNO", "Dalla riga a: colonna 2 → pin 6, colonna 6 → pin 7, colonna 10 → pin 8, colonna 14 → pin 9."),
         ("4 LED in riga c", "Rosso con il lungo in 19 (corto in 20), verde 21-22, blu 23-24, giallo 25-26. Ogni corto → resistenza 220 Ω → riga – in basso."),
         ("LED → UNO", "Colonna 19 → pin 2, 21 → pin 3, 23 → pin 4, 25 → pin 5."),
         ("Buzzer passivo in riga c, colonne 27 e 29", "+ in 27 → pin 10, colonna 29 → riga –."),
         ("Masse", "Unisci la riga – in alto con quella in basso, e GND della UNO → riga –."),
        ] + carica("«Gioco Simon»") + [
         ("Gioca", "Le luci girano in attesa: premi un pulsante per iniziare. Guarda la sequenza e ripetila. Ogni turno si aggiunge una luce e va un po' più veloce."),
        ],
        [("Pulsante rosso (col. 2)", "pin 6", ""), ("Pulsante verde (col. 6)", "pin 7", ""), ("Pulsante blu (col. 10)", "pin 8", ""),
         ("Pulsante giallo (col. 14)", "pin 9", ""), ("Pulsanti, col. 4, 8, 12, 16 (riga a)", "riga – in alto", "diagonale"),
         ("LED rosso, lungo (col. 19)", "pin 2", ""), ("LED verde, lungo (col. 21)", "pin 3", ""), ("LED blu, lungo (col. 23)", "pin 4", ""),
         ("LED giallo, lungo (col. 25)", "pin 5", ""), ("Corti dei LED", "220 Ω → riga –", "col. 20, 22, 24, 26"),
         ("Buzzer + (col. 27)", "pin 10", ""), ("Buzzer (col. 29)", "riga –", ""), ("Riga – in alto", "riga – in basso", ""),
         ("GND della UNO", "riga –", "")],
        [("Un pulsante accende il LED sbagliato", "Hai scambiato due fili dei pulsanti o dei LED: segui la tabella, rosso-verde-blu-giallo nell'ordine."),
         ("La partita non parte", "Controlla la massa dei pulsanti (riga – in alto collegata a quella in basso)."),
         ("Il gioco dice «sbagliato» subito", "Un pulsante è girato e risulta sempre premuto: usa piedini opposti in diagonale.")])


# ------------------------------------------------------------------ 21 DADO
def guida_dado():
    def dis():
        foro, p = dis_settesegmenti(ncol=26)
        due_piedini(foro, 22, 24, "h", corpo_tilt, "inclinazione")
        ponticello(foro(24, "j"), foro(24, "-b"))
        wire(foro(22, "j"), p["D2"], GREEN, (foro(22, "j")[0], 220), (p["D2"][0] + 30, 250), w=2.6)
        etichetta(p["D2"][0] + 8, 190, "2", GREEN)
    return guida_autonoma("Dado elettronico", "Scuoti la breadboard e il display tira un dado", 21,
        ["tutto il montaggio del progetto 14 «Display a 7 segmenti» (74HC595, display, 8 resistenze)",
         "il sensore di inclinazione e 2 cavetti maschio-maschio",
         "la batteria 9V con spinotto"],
        [("Difficoltà", "Difficile"), ("Tempo", "45 minuti"), ("Fili da collegare", "~17 + 8 resistenze")],
        dis,
        [("Monta il display come nel progetto 14", "Se l'hai già montato, lascialo com'è: aggiungi solo il sensore di inclinazione."),
         ("Sensore di inclinazione in riga c, colonne 22 e 24", "Colonna 22 → pin 2, colonna 24 → riga –. Non ha un verso."),
        ] + carica("«Dado elettronico»") + [
         ("Tira il dado", "Scuoti la breadboard avanti e indietro 2-3 volte: il display fa girare i numeri e si ferma su uno da 1 a 6."),
        ],
        [("74HC595 e display", "come progetto 14", ""), ("Inclinazione (col. 22)", "pin 2", ""), ("Inclinazione (col. 24)", "riga –", "")],
        [("Non parte quando scuoto", "Scuoti con più decisione: servono almeno tre cambi del sensore in poco tempo."),
         ("Numeri strani o display spento", "Il display potrebbe essere ad anodo comune: comuni a + e scegli «Anodo comune» nella pagina del progetto (resta salvato)."),
         ("Parte da solo", "Il sensore è in bilico: appoggia la breadboard su un piano.")])


# ------------------------------------------------------------------ 22 METRO
def guida_metro():
    def dis():
        foro, p = dis_lcd()
        # pulsante «volante»: due piedini opposti infilati nei lati femmina di due cavetti
        bx, by = 520, 250
        c.setFillColor(HexColor("#2b2b2b")); c.roundRect(bx - 14, by - 14, 28, 28, 3, stroke=0, fill=1)
        c.setFillColor(HexColor("#555555")); c.circle(bx, by, 8, stroke=0, fill=1)
        text(bx, by + 20, "blocca", 7, "SB", GREY, "c")
        wire((bx - 14, by - 14), p["D4"], GREEN, (bx - 60, by - 40), (p["D4"][0] + 60, 240), w=2.6)
        wire((bx + 14, by + 14), foro(31, "-b"), BLK, (bx + 40, by + 30), (foro(31, "-b")[0] + 20, foro(31, "-b")[1] - 10), w=2.6)
        s_ = sr04_modulo(415, 110)
        wire(s_["Trig"], p["D2"], AZZ, (s_["Trig"][0], 60), (p["D2"][0] + 60, 280))
        wire(s_["Echo"], p["D3"], ORANGE, (s_["Echo"][0], 50), (p["D3"][0] + 50, 290))
        wire(s_["Vcc"], foro(29, "+b"), RED, (s_["Vcc"][0] - 10, 200), (foro(29, "+b")[0], foro(29, "+b")[1] - 30), w=2.6)
        wire(s_["Gnd"], foro(30, "-b"), BLK, (s_["Gnd"][0] + 10, 210), (foro(30, "-b")[0], foro(30, "-b")[1] - 30), w=2.6)
        etichetta(p["D4"][0] + 26, 190, "2 · 3 · 4", GREEN)
    return guida_autonoma("Metro portatile", "Misura le distanze con gli ultrasuoni e le scrive sul display", 22,
        ["tutto il montaggio del progetto 15 «Display LCD»",
         "il sensore a ultrasuoni HC-SR04 e 4 cavetti maschio-femmina",
         "1 pulsante e 2 cavetti maschio-femmina",
         "la batteria 9V con spinotto"],
        [("Difficoltà", "Difficile"), ("Tempo", "50 minuti"), ("Fili da collegare", "~21")],
        dis,
        [("Monta il display come nel progetto 15", "Il potenziometro del contrasto resta nelle colonne 22-24-26."),
         ("Pulsante «blocca» con due cavetti maschio-femmina", "Il display copre la scanalatura, quindi il pulsante resta fuori dalla breadboard: infila due piedini opposti in diagonale nei lati femmina di due cavetti. Un cavetto → pin 4, l'altro → riga –."),
         ("Sensore HC-SR04 (maschio-femmina)", "Vcc → riga +, Gnd → riga –, Trig → pin 2, Echo → pin 3."),
        ] + carica("«Metro portatile»") + [
         ("Misura", "Punta il sensore verso una parete: la distanza compare sul display, con una barra che arriva a 2 metri. Premi il pulsante per bloccare la misura."),
        ],
        [("Display LCD", "come progetto 15", "pin 7-12"), ("HC-SR04 – Vcc / Gnd", "riga + / riga –", "maschio-femmina"),
         ("HC-SR04 – Trig", "pin 2", "maschio-femmina"), ("HC-SR04 – Echo", "pin 3", "maschio-femmina"),
         ("Pulsante, un piedino", "pin 4", "maschio-femmina"), ("Pulsante, piedino in diagonale", "riga –", "maschio-femmina")],
        [("«Fuori portata» fisso", "Controlla Trig (pin 2) ed Echo (pin 3): in questo progetto sono diversi dal progetto 11."),
         ("Il display è vuoto", "Gira il potenziometro del contrasto."),
         ("Il pulsante non blocca", "Usa due piedini opposti in diagonale.")])


# ------------------------------------------------------------------ 23 LAMPADA
def guida_lampada():
    def dis():
        foro = bb(70, 300, 22, sopra=False)
        p = uno(85, 40, hl={"A0": ORANGE, "A1": VIOLA, "D9": YEL, "D10": YEL, "GNDT": BLK, "5V": RED}, s=0.86)
        def corpo_ldr(cx, cy):
            c.setFillColor(HexColor("#e8a05a")); c.circle(cx, cy, 11, stroke=0, fill=1)
            c.setStrokeColor(HexColor("#8a3b12")); c.setLineWidth(1.2)
            pth = c.beginPath(); pth.moveTo(cx - 7, cy + 4)
            for i in range(4): pth.lineTo(cx + 7 if i % 2 == 0 else cx - 7, cy + 4 - (i + 1) * 2.5)
            c.drawPath(pth, stroke=1, fill=0)
        due_piedini(foro, 3, 5, "h", corpo_ldr, "fotoresistenza")
        ponticello(foro(3, "j"), foro(3, "+b"), RED)
        resistenza(foro(5, "i"), foro(9, "i"), B10K)
        ponticello(foro(9, "j"), foro(9, "-b"))
        potenziometro_bb(foro, 11)
        ponticello(foro(11, "j"), foro(11, "+b"), RED); ponticello(foro(15, "j"), foro(15, "-b"))
        led_bb(foro, 18, "#f4f4f4", "bianco"); res_vert(foro, 19)
        led_bb(foro, 20, "#f4f4f4", "bianco"); res_vert(foro, 21)
        wire(foro(5, "j"), p["A0"], ORANGE, (foro(5, "j")[0] - 60, 200), (p["A0"][0] + 90, 20), w=2.6)
        wire(foro(13, "j"), p["A1"], VIOLA, (foro(13, "j")[0] - 40, 200), (p["A1"][0] + 100, 10), w=2.6)
        wire(foro(18, "j"), p["D9"], YEL, (foro(18, "j")[0], 240), (p["D9"][0], 260), w=2.6)
        wire(foro(20, "j"), p["D10"], YEL, (foro(20, "j")[0] + 10, 240), (p["D10"][0] - 10, 260), w=2.6)
        piede_5v_gnd(p, foro)
        etichetta(p["A0"][0] + 4, 22, "A0 · A1", ORANGE); etichetta(p["D9"][0] + 4, 202, "9 · 10", YEL)
    return guida_autonoma("Lampada notturna", "I LED si accendono da soli quando fa buio", 23,
        ["la UNO, il cavo USB blu, la breadboard e la batteria 9V con spinotto",
         "la fotoresistenza e 1 resistenza da 10 kΩ",
         "il potenziometro da 10 kΩ",
         "2 LED bianchi, 2 resistenze da 220 Ω e 9 cavetti maschio-maschio"],
        [("Difficoltà", "Media"), ("Tempo", "30 minuti"), ("Fili da collegare", "9 + 3 resistenze")],
        dis,
        [("Fotoresistenza in riga c, colonne 3 e 5", "Colonna 3 → riga +. Resistenza 10 kΩ da b5 a b9, colonna 9 → riga –. Colonna 5 → A0."),
         ("Potenziometro in riga c, colonne 11, 13, 15", "11 → riga +, 15 → riga –, centrale (13) → A1."),
         ("2 LED bianchi", "Lungo in 18 (corto 19) e lungo in 20 (corto 21). Ogni corto → 220 Ω → riga –. Colonna 18 → pin 9, colonna 20 → pin 10."),
         ("Alimentazione", "5V della UNO → riga +, GND → riga –."),
        ] + carica("«Lampada notturna»") + [
         ("Regola la soglia", "Gira la manopola finché i LED sono spenti con la luce della stanza. Copri la fotoresistenza: dopo un attimo i LED si accendono piano piano."),
        ],
        [("Fotoresistenza (col. 3)", "riga +", ""), ("Fotoresistenza (col. 5)", "A0", ""), ("Resistenza 10 kΩ", "da i5 a i9", ""),
         ("Colonna 9", "riga –", ""), ("Potenziometro, esterni (col. 11, 15)", "riga + / riga –", ""), ("Potenziometro, centrale (col. 13)", "A1", ""),
         ("LED, lunghi (col. 18, 20)", "pin 9 / pin 10", ""), ("LED, corti (col. 19, 21)", "220 Ω → riga –", ""), ("5V / GND della UNO", "riga + / riga –", "")],
        [("I LED restano sempre accesi", "La soglia è troppo alta: gira la manopola dall'altra parte."),
         ("I LED non si accendono mai", "Gira la manopola, e controlla che il filo di A0 parta dalla colonna 5."),
         ("Si accendono e spengono di continuo", "La luce dei LED illumina la fotoresistenza: allontanali o girali dall'altra parte.")])


# ------------------------------------------------------------------ 24 CRONOMETRO
def guida_cronometro():
    def dis():
        foro = bb(30, 290, 29)
        p = uno(70, 30, hl={"D12": AZZ, "D11": VIOLA, "D9": ORANGE, "D2": RED, "D3": RED, "D4": RED, "D5": RED, "D6": GREEN, "D7": YEL, "GNDT": BLK, "5V": RED}, s=0.80)
        pin = chip_bb(foro, 2, "74HC595")
        def fp(n, r=None):
            cc, half = pin(n)
            return foro(cc, r or ("a" if half == "e" else "j"))
        ponticello(fp(16), foro(pin(16)[0], "+s"), RED); ponticello(fp(10), foro(pin(10)[0], "+s"), RED)
        ponticello(fp(13), foro(pin(13)[0], "-s"), BLK); ponticello(fp(8), foro(pin(8)[0], "-b"), BLK)
        # display 4 cifre: colonne 13-18. In basso pin 1..6, in alto 12..7
        def dpin(n):
            return (12 + n, "f") if n <= 6 else (13 + 12 - n, "e")
        xa, xb = foro(13, "e")[0] - 9, foro(18, "e")[0] + 9
        ya, yb = foro(13, "f")[1] - 4, foro(13, "e")[1] + 4
        c.setFillColor(HexColor("#2b2b2b")); c.rect(xa - 10, ya - 12, xb - xa + 20, yb - ya + 24, stroke=0, fill=1)
        text((xa + xb) / 2, (ya + yb) / 2 - 5, "8.8.8.8", 13, "SB", HexColor("#ff5a4a"), "c")
        nomi = {1: "e", 2: "d", 3: "dp", 4: "c", 5: "g", 6: "D4", 7: "b", 8: "D3", 9: "D2", 10: "f", 11: "a", 12: "D1"}
        for n in range(1, 13):
            cc, r = dpin(n); fx, fy = foro(cc, r)
            text(fx, fy + (-14 if r == "f" else 8), nomi[n], 6, "SB", HexColor("#c03030"), "c")
        seg_q = {"a": 15, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "dp": 7}
        seg_pin = {"e": 1, "d": 2, "dp": 3, "c": 4, "g": 5, "b": 7, "f": 10, "a": 11}
        colori = {"a": "#1f8fd1", "b": "#2a9d3a", "c": "#d4a100", "d": "#7b3fc4", "e": "#d63384", "f": "#f28c18", "g": "#555555", "dp": "#1b7a3a"}
        for k, (s_, q) in enumerate(seg_q.items()):
            cc, half = pin(q)
            a = foro(cc, "c" if half == "e" else "h")
            dc, dr = dpin(seg_pin[s_])
            b = foro(dc, "c" if dr == "e" else "h")
            up = 1 if half == "e" else -1
            wire_res(a, b, HexColor(colori[s_]), (a[0], a[1] + up * (14 + k * 4)), (b[0], b[1] + (1 if dr == "e" else -1) * (14 + k * 4)),
                     bande=["#7a4a21", "#111111", "#111111", "#7a4a21", "#7a4a21"])
        # cifre → pin 2..5
        for d, pn in [(12, "D2"), (9, "D3"), (8, "D4"), (6, "D5")]:
            cc, r = dpin(d)
            a = foro(cc, "a" if r == "e" else "j")
            wire(a, p[pn], RED, (a[0] + 20, a[1] + (30 if r == "e" else -30)), (p[pn][0], 250), w=2)
        # pulsanti
        for cb, pn, col in [(21, "D6", GREEN), (25, "D7", YEL)]:
            pulsante_bb(foro, cb)
            ponticello(foro(cb + 2, "a"), foro(cb + 2, "-s"))
            wire(foro(cb, "j"), p[pn], col, (foro(cb, "j")[0], 220), (p[pn][0] + 20, 250), w=2.4)
        text(foro(22, "a")[0], foro(22, "a")[1] + 18, "avvia/ferma", 6.5, "SB", GREEN, "c")
        text(foro(26, "a")[0], foro(26, "a")[1] + 18, "azzera", 6.5, "SB", YEL, "c")
        wire(fp(14), p["D12"], AZZ, (fp(14)[0] - 60, fp(14)[1] + 10), (p["D12"][0] - 70, 230))
        wire(fp(12), p["D11"], VIOLA, (fp(12)[0] - 90, fp(12)[1] + 20), (p["D11"][0] - 60, 240))
        wire(fp(11), p["D9"], ORANGE, (fp(11)[0] - 110, fp(11)[1] + 30), (p["D9"][0] - 50, 250))
        wire(foro(29, "+s"), foro(29, "+b"), RED, (foro(29, "+s")[0] + 34, foro(29, "+s")[1]), (foro(29, "+b")[0] + 34, foro(29, "+b")[1]), w=2.4)
        wire(foro(28, "-s"), foro(28, "-b"), BLK, (foro(28, "-s")[0] + 24, foro(28, "-s")[1]), (foro(28, "-b")[0] + 24, foro(28, "-b")[1]), w=2.4)
        wire(p["GNDT"], foro(1, "-b"), BLK, (p["GNDT"][0] - 10, 240), (foro(1, "-b")[0], 230))
        wire(p["5V"], foro(1, "+b"), RED, (p["5V"][0] - 30, 0), (5, 200))
        etichetta(p["GNDT"][0] - 18, 196, "GND", BLK)
    return guida_autonoma("Cronometro a 4 cifre", "Un cronometro vero, con il display a 4 cifre e due pulsanti", 24,
        ["la UNO, il cavo USB blu, la breadboard e la batteria 9V con spinotto",
         "il chip 74HC595 e il display a 4 cifre (12 piedini)",
         "8 resistenze da 1 kΩ (marrone-nero-nero-marrone-marrone) e 2 pulsanti",
         "circa 25 cavetti maschio-maschio"],
        [("Difficoltà", "Molto difficile"), ("Tempo", "1 ora"), ("Fili da collegare", "~25 + 8 resistenze")],
        dis,
        [("Chip 74HC595 a cavallo della scanalatura, colonne 2-9", "Tacca a sinistra. Alimentazione e 3 segnali come nel progetto 13: 16 e 10 → +, 13 → – in alto, 8 → – in basso, 14 → pin 12, 12 → pin 11, 11 → pin 9."),
         ("Display a cavallo della scanalatura, colonne 13-18", "Con i punti decimali in basso. In basso da sinistra: e, d, punto, c, g, D4. In alto da sinistra: D1, a, f, D2, D3, b."),
         ("8 resistenze da 1 kΩ tra chip e segmenti", "Q0 → a, Q1 → b, Q2 → c, Q3 → d, Q4 → e, Q5 → f, Q6 → g, Q7 → punto. Da 1 kΩ, non 220: proteggono i pin delle cifre."),
         ("Cifre → UNO", "D1 → pin 2, D2 → pin 3, D3 → pin 4, D4 → pin 5 (con un filo, senza resistenza)."),
         ("2 pulsanti, colonne 21-23 e 25-27", "Colonna 21 → pin 6 (avvia/ferma), colonna 25 → pin 7 (azzera). Colonne 23 e 27 (riga j, diagonale) → riga – in alto."),
         ("Unisci le righe e alimenta", "Righe + e – in alto con quelle in basso; 5V della UNO → riga +, GND → riga –."),
        ] + carica("«Cronometro a 4 cifre»") + [
         ("Cronometra", "Premi avvia/ferma per partire e fermarti, azzera per tornare a zero. Fino a 99,99 secondi mostra i centesimi, poi minuti e secondi."),
        ],
        [("74HC595 – 16, 10", "riga + in alto", "col. 2, 8"), ("74HC595 – 13", "riga – in alto", "col. 5"), ("74HC595 – 8", "riga – in basso", "col. 9"),
         ("74HC595 – 14 / 12 / 11", "pin 12 / 11 / 9", "col. 4 / 6 / 7"), ("Q0 (15) … Q7 (7)", "1 kΩ → a, b, c, d, e, f, g, punto", ""),
         ("Display D1 (in alto, 1°)", "pin 2", "col. 13"), ("Display D2 (in alto, 4°)", "pin 3", "col. 16"),
         ("Display D3 (in alto, 5°)", "pin 4", "col. 17"), ("Display D4 (in basso, 6°)", "pin 5", "col. 18"),
         ("Pulsante avvia/ferma (col. 21)", "pin 6", ""), ("Pulsante azzera (col. 25)", "pin 7", ""),
         ("Pulsanti (col. 23, 27, riga a)", "riga – in alto", "diagonale"), ("Righe in alto", "righe in basso", ""),
         ("5V / GND della UNO", "riga + / riga –", "")],
        [("Display spento o con segni strani", "Il display potrebbe essere ad anodo comune: nella pagina del progetto scegli «Anodo comune» (resta salvato)."),
         ("Una cifra non si accende", "Controlla il filo della sua cifra (D1-D4 ai pin 2-5)."),
         ("Le cifre sono tutte uguali o tremolano", "Normale se guardi con la fotocamera del telefono: le cifre si accendono una alla volta molto velocemente.")],
        note=["Le 4 cifre condividono gli stessi 8 fili dei segmenti: la UNO accende una cifra alla volta, così velocemente "
              "(centinaia di volte al secondo) che l'occhio le vede tutte accese insieme. Si chiama «multiplexing».",
              "È il progetto con più fili di tutti: procedi una riga della tabella alla volta."])


# ------------------------------------------------------------------ 25 SERVO + TELECOMANDO
def guida_servoir():
    def dis():
        r = rotaie(50, 390)
        sv = servo_disegno(495, 320)
        ir = modulo(300, 470, 80, 60, "Ricevitore IR", ["G", "R", "Y"], "#1e1e1e")
        disegno_telecomando(470, 430)
        for k in range(3):
            c.setStrokeColor(HexColor("#d43c3c")); c.setLineWidth(1.2); c.setDash(3, 3)
            c.line(470, 540 - k * 10, 384, 515 - k * 5)
        c.setDash()
        p = uno(80, 60, hl={"D9": ORANGE, "D11": BLUEW, "GNDT": BLK, "5V": RED}, s=0.9)
        wire(p["5V"], r(1, "+"), RED, (60, 10), (20, 360))
        wire(p["GNDT"], r(3, "-"), BLK, (p["GNDT"][0], 320), (r(3, "-")[0], 340))
        wire(sv["vcc"], r(15, "+"), RED, (sv["vcc"][0] - 30, 380), (r(15, "+")[0], 380))
        wire(sv["gnd"], r(16, "-"), BROWN, (sv["gnd"][0] - 10, 360), (r(16, "-")[0], 360))
        wire(sv["sig"], p["D9"], ORANGE, (sv["sig"][0] - 120, 300), (p["D9"][0], 300))
        wire(ir["R"], r(12, "+"), RED, (ir["R"][0], 450), (r(12, "+")[0], 460), w=2.6)
        wire(ir["G"], r(10, "-"), BLK, (ir["G"][0] - 10, 450), (r(10, "-")[0], 455), w=2.6)
        wire(ir["Y"], p["D11"], BLUEW, (ir["Y"][0] + 90, 400), (p["D11"][0] + 20, 300), w=2.6)
        etichetta(p["D9"][0] - 14, 270, "9", ORANGE); etichetta(p["D11"][0] - 4, 282, "11", BLUEW)
        etichetta(p["GNDT"][0] - 18, 270, "GND", BLK); etichetta(p["5V"][0] - 26, 40, "5V", RED)
    return guida_autonoma("Servo col telecomando", "Muovi il servo con il telecomando, senza telefono", 25,
        ["la UNO, il cavo USB blu, la breadboard (solo il bordo + e –) e la batteria 9V con spinotto",
         "il servo SG90, il ricevitore a infrarossi e il telecomando",
         "3 cavetti maschio-femmina e 5 maschio-maschio"],
        [("Difficoltà", "Facile"), ("Tempo", "20 minuti"), ("Fili da collegare", "8")],
        dis,
        [("Alimenta il bordo della breadboard", "5V della UNO → riga +, GND → riga –."),
         ("Servo", "Rosso → riga +, marrone → riga –, arancione → pin 9."),
         ("Ricevitore IR (maschio-femmina)", "G → riga –, R → riga +, Y → pin 11."),
        ] + carica("«Servo col telecomando»") + [
         ("Usa il telecomando", "Tasti 0-9: angolo da 0° a 180°. ⏮ ⏭: ±10°. VOL– VOL+: ±1° (tieni premuto per continuare). ⏯: movimento automatico. ⏻: torna al centro."),
        ],
        [("5V / GND della UNO", "riga + / riga –", ""), ("Servo – rosso / marrone", "riga + / riga –", ""),
         ("Servo – arancione", "pin 9", ""), ("Ricevitore – G / R", "riga – / riga +", "maschio-femmina"),
         ("Ricevitore – Y", "pin 11", "maschio-femmina")],
        [("Il servo non risponde al telecomando", "Togli la linguetta di plastica dal telecomando e punta il ricevitore da vicino."),
         ("Il servo trema", "A batteria 9V va meglio che col telefono; se trema ancora, la batteria è scarica."),
         ("Risponde solo ogni tanto", "Il servo disturba un po' il ricevitore: tieni i loro fili separati.")])


GUIDE = {"blink": guida_blink, "servo": guida_servo, "rgb": guida_rgb, "luce": guida_luce, "buzzer": guida_buzzer,
         "semaforo": guida_semaforo, "pulsanti": guida_pulsanti, "potenziometro": guida_potenziometro, "meteo": guida_meteo,
         "joystick": guida_joystick, "allarme": guida_allarme, "telecomando": guida_telecomando, "registro": guida_registro,
         "settesegmenti": guida_settesegmenti, "lcd": guida_lcd, "ventilatore": guida_ventilatore, "passo": guida_passo,
         "parcheggio": guida_parcheggio, "termometro": guida_termometro, "simon": guida_simon, "dado": guida_dado,
         "metro": guida_metro, "lampada": guida_lampada, "cronometro": guida_cronometro, "servoir": guida_servoir}
TITOLI = {"blink": "LED integrato", "servo": "Servo + sensore distanza", "rgb": "LED RGB", "luce": "Sensore di luce", "buzzer": "Buzzer",
          "semaforo": "Semaforo", "pulsanti": "Pulsanti e inclinazione", "potenziometro": "Manopola", "meteo": "Stazione meteo",
          "joystick": "Joystick", "allarme": "Allarme antifurto", "telecomando": "Telecomando a infrarossi", "registro": "8 LED con il 74HC595",
          "settesegmenti": "Display a 7 segmenti", "lcd": "Display LCD", "ventilatore": "Ventilatore", "passo": "Motore passo-passo",
          "parcheggio": "Sensore di parcheggio", "termometro": "Termometro con LCD", "simon": "Gioco Simon", "dado": "Dado elettronico",
          "metro": "Metro portatile", "lampada": "Lampada notturna", "cronometro": "Cronometro a 4 cifre", "servoir": "Servo col telecomando"}
NUM = {"blink": 1, "semaforo": 2, "pulsanti": 3, "buzzer": 4, "rgb": 5, "potenziometro": 6, "luce": 7, "meteo": 8, "joystick": 9,
       "allarme": 10, "servo": 11, "telecomando": 12, "registro": 13, "settesegmenti": 14, "lcd": 15, "ventilatore": 16, "passo": 17,
       "parcheggio": 18, "termometro": 19, "simon": 20, "dado": 21, "metro": 22, "lampada": 23, "cronometro": 24, "servoir": 25}

if __name__ == "__main__":
    import io
    out = sys.argv[1]
    solo = sys.argv[2:] or list(GUIDE)
    os.makedirs(out, exist_ok=True)
    for k in solo:
        f = GUIDE[k]
        # primo giro per contare le pagine delle guide a impaginazione automatica
        c = canvas.Canvas(io.BytesIO(), pagesize=A4)
        guida_generica.tot = 99
        tot = f()
        guida_generica.tot = tot if isinstance(tot, int) else 2
        c = canvas.Canvas(f"{out}/{k}.pdf", pagesize=A4)
        c.setTitle(f"UNO Lab - Progetto {NUM[k]}: {TITOLI[k]}")
        f()
        c.save()
        print("ok", k, guida_generica.tot)
