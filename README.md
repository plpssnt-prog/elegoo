# UNO Lab

Web app per caricare progetti di test sulla Elegoo UNO R3 dal telefono (Chrome su Android, via USB OTG) o dal PC (Chrome/Edge), e comandarli dalla pagina relativa.

## Come funziona
- **Collega**: la pagina apre la porta USB della UNO. Ogni sketch all'avvio stampa `READY <id>`, quindi l'app sa sempre quale progetto c'è sulla scheda.
- **Carica sulla scheda**: scarica `public/firmware/<id>.hex` e lo scrive sulla UNO col protocollo del bootloader (STK500/Optiboot, lo stesso dell'IDE Arduino), poi verifica e apre la pagina di comando.
- **Comandi**: ogni progetto ha la sua pagina; parla con lo sketch con righe di testo (es. `A90`, `C255,0,0`).

## Struttura
```
sketches/<id>/<id>.ino     sorgente di ogni progetto
public/firmware/<id>.hex   firmware compilati (li genera la GitHub Action)
public/guide/<id>.pdf      guida per principianti con i disegni dei collegamenti (29 progetti, 5 livelli; il livello 5 funziona anche a batteria)
public/js/progetti.js      elenco progetti + pagine di comando
public/js/flasher.js       programmazione della UNO
public/js/link.js          collegamento WebUSB / Web Serial
```

## Aggiungere un progetto
1. Crea `sketches/<id>/<id>.ino`. Deve: usare `Serial.begin(115200)`, stampare `READY <id>` in `setup()`, rispondere `ID <id>` al comando `ID?`.
2. Aggiungi in `public/js/progetti.js` un oggetto con lo stesso `id`, i collegamenti e la funzione `monta()` con i controlli.
3. Push su GitHub: la Action "Compila firmware" crea il `.hex` e Cloudflare ripubblica il Worker.

## Pubblicazione
Worker statico (`wrangler.jsonc` → cartella `public`). Serve HTTPS: workers.dev va bene.

## App installabile (PWA)
In Chrome su Android: menu ⋮ → «Installa app» (o il pulsante «Installa» in alto). Funziona anche offline;
con la rete scarica sempre la versione più recente.

## Aggiornare guide e programmi
Le guide PDF si rigenerano con `python3 strumenti/guide.py public/guide` (serve `reportlab`).
Dopo aver cambiato guide o programmi, aumenta `VERSIONE` in `public/js/versione.js`: così il telefono scarica le copie nuove.

## App Android (Capacitor)

La cartella `app/` contiene l'app Android: apre il sito `https://elegoo.pl-pssnt.workers.dev` (quindi si aggiorna da sola come la PWA) e aggiunge
- **USB nativo** (`UnoSerialPlugin.java`, senza librerie esterne): nella WebView di Android WebUSB non esiste, quindi il plugin parla direttamente con la porta seriale CDC del chip ATmega16U2 (stesse funzioni del driver WebUSB: segnali DTR/RTS, invio, ricezione). In `public/js/nativo.js` c'è il trasporto `UsbNativo` usato da `link.js` quando la pagina gira dentro l'app.
- **Apertura automatica**: quando colleghi la UNO, Android propone di aprire UNO Lab (filtro USB in `res/xml/device_filter.xml`); scegliendo «Sempre» non chiede più il permesso.
- Le guide PDF si aprono in Chrome (plugin `@capacitor/browser`).

GitHub Actions (`.github/workflows/android.yml`) costruisce l'APK a ogni modifica di `app/` e lo pubblica nella release
[`app-latest`](https://github.com/plpssnt-prog/elegoo/releases/download/app-latest/UNO-Lab.apk). La chiave di firma
`unolab-debug.keystore` è nel repo apposta, così ogni APK si installa sopra il precedente.
