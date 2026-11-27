// Ponte verso le parti native dell'app Android UNO Lab (Capacitor). Nella PWA in Chrome è tutto spento.
const cap = window.Capacitor;

export const isApp = !!(cap && typeof cap.nativePromise === "function");
export const APK_URL = "https://github.com/plpssnt-prog/elegoo/releases/download/app-latest/UNO-Lab.apk";

const chiama = (metodo, opz = {}) => cap.nativePromise("UnoSerial", metodo, opz);
const ascolta = (evento, cb) => cap.addListener("UnoSerial", evento, cb);

const daB64 = s => Uint8Array.from(atob(s), ch => ch.charCodeAt(0));
const aB64 = u8 => { let s = ""; for (const b of u8) s += String.fromCharCode(b); return btoa(s); };

// Trasporto USB nativo: stesse funzioni dei trasporti WebUSB / Web Serial di link.js
export class UsbNativo {
  static disponibile() { return isApp; }
  static async scegli() { return { chiedi: true }; }
  static async giaAutorizzato() { return { chiedi: false }; }
  constructor(o) { this.o = o; this.nome = "USB (app)"; }

  async open() {
    const r = await chiama("connetti", { chiedi: this.o.chiedi });
    if (!r || !r.ok) throw Object.assign(new Error((r && r.motivo) || "nessuna scheda"), { name: this.o.chiedi ? "Error" : "NotFoundError" });
    this.aperto = true;
  }
  setSignals(dtr, rts) { return chiama("segnali", { dtr, rts }); }
  write(u8) { return chiama("scrivi", { b64: aB64(u8) }); }

  readLoop(onData) {
    return new Promise((ok, ko) => {
      this.fine = ok;
      this.h1 = ascolta("dati", e => e && e.b64 && onData(daB64(e.b64)));
      this.h2 = ascolta("staccato", () => { this.aperto = false; ko(new Error("cavo scollegato")); });
    });
  }

  async close() {
    this.aperto = false;
    for (const h of [this.h1, this.h2]) { try { (await h)?.remove(); } catch {} }
    try { await chiama("chiudi"); } catch {}
    this.fine?.();
  }
}

// Quando la UNO viene collegata con l'app già aperta
export function quandoAttaccata(cb) { if (isApp) ascolta("attaccato", cb); }

// Le guide PDF: nella WebView non si aprono, le passa a Chrome
export function apriEsterno(url) {
  if (!isApp) return false;
  cap.nativePromise("Browser", "open", { url: new URL(url, location.href).href }).catch(() => { location.href = url; });
  return true;
}
