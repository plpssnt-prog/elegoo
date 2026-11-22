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
public/guide/<id>.pdf      guida per principianti con i disegni dei collegamenti (17 progetti, 4 livelli)
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
