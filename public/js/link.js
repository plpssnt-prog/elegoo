// Collegamento seriale con la UNO.
// Android: WebUSB con un driver CDC-ACM minimale (chip ATmega16U2).
// PC: Web Serial standard (Chrome/Edge).

import { UsbNativo } from "./nativo.js";

export const BAUD = 115200;
const enc = new TextEncoder();
const dec = new TextDecoder();
export const sleep = ms => new Promise(r => setTimeout(r, ms));

class UsbCdc {
  static disponibile() { return !!navigator.usb; }
  static async scegli() { return navigator.usb.requestDevice({ filters: [] }); }
  static async giaAutorizzato() {
    const d = await navigator.usb.getDevices();
    return d.length ? d[0] : null;
  }
  constructor(dev) { this.dev = dev; this.nome = "WebUSB"; }

  async open() {
    const dev = this.dev;
    await dev.open();
    if (dev.configuration === null) await dev.selectConfiguration(1);
    const ifs = dev.configuration.interfaces;
    const comm = ifs.find(i => i.alternates[0].interfaceClass === 0x02);
    const data = ifs.find(i => i.alternates[0].interfaceClass === 0x0a);
    if (!data) throw new Error("questo dispositivo non è una porta seriale");
    this.commIf = comm ? comm.interfaceNumber : 0;
    if (comm) { try { await dev.claimInterface(this.commIf); } catch {} }
    await dev.claimInterface(data.interfaceNumber);
    const eps = data.alternates[0].endpoints;
    this.epIn = eps.find(e => e.direction === "in" && e.type === "bulk").endpointNumber;
    this.epOut = eps.find(e => e.direction === "out" && e.type === "bulk").endpointNumber;
    const lc = new ArrayBuffer(7), v = new DataView(lc);
    v.setUint32(0, BAUD, true); v.setUint8(4, 0); v.setUint8(5, 0); v.setUint8(6, 8);
    await this._ctrl(0x20, 0, lc);
    this.aperto = true;
  }
  _ctrl(request, value, data) {
    const s = { requestType: "class", recipient: "interface", request, value, index: this.commIf };
    return data ? this.dev.controlTransferOut(s, data) : this.dev.controlTransferOut(s);
  }
  setSignals(dtr, rts) { return this._ctrl(0x22, (dtr ? 1 : 0) | (rts ? 2 : 0)); }
  async readLoop(onData) {
    while (this.aperto) {
      try {
        const r = await this.dev.transferIn(this.epIn, 64);
        if (r.data && r.data.byteLength) onData(new Uint8Array(r.data.buffer, r.data.byteOffset, r.data.byteLength));
      } catch (e) { if (this.aperto) throw e; }
    }
  }
  write(u8) { return this.dev.transferOut(this.epOut, u8); }
  async close() { this.aperto = false; try { await this.dev.close(); } catch {} }
}

class SerialPortT {
  static disponibile() { return !!navigator.serial; }
  static async scegli() { return navigator.serial.requestPort(); }
  static async giaAutorizzato() {
    const p = await navigator.serial.getPorts();
    return p.length ? p[0] : null;
  }
  constructor(port) { this.port = port; this.nome = "Web Serial"; }
  async open() {
    await this.port.open({ baudRate: BAUD, bufferSize: 4096 });
    this.writer = this.port.writable.getWriter();
    this.aperto = true;
  }
  setSignals(dtr, rts) { return this.port.setSignals({ dataTerminalReady: dtr, requestToSend: rts }); }
  async readLoop(onData) {
    while (this.aperto && this.port.readable) {
      this.reader = this.port.readable.getReader();
      try {
        for (;;) {
          const { value, done } = await this.reader.read();
          if (done) break;
          if (value) onData(value);
        }
      } finally { this.reader.releaseLock(); }
    }
  }
  write(u8) { return this.writer.write(u8); }
  async close() {
    this.aperto = false;
    try { await this.reader?.cancel(); } catch {}
    try { this.writer.releaseLock(); } catch {}
    try { await this.port.close(); } catch {}
  }
}

function tipoTrasporto() {
  if (UsbNativo.disponibile()) return UsbNativo;      // app Android: USB nativo
  const android = /Android/i.test(navigator.userAgent);
  if (android && UsbCdc.disponibile()) return UsbCdc;
  if (SerialPortT.disponibile()) return SerialPortT;
  if (UsbCdc.disponibile()) return UsbCdc;
  return null;
}

export function browserSupportato() { return !!tipoTrasporto(); }

// Collegamento con modalità testo (righe) e modalità binaria (programmazione)
export class Link extends EventTarget {
  constructor() {
    super();
    this.t = null;
    this.raw = [];
    this.attesa = null;
    this.modo = "testo";
    this.riga = "";
  }
  get connesso() { return !!this.t; }

  // auto = true: usa un dispositivo già autorizzato senza mostrare il selettore
  async connetti(auto = false) {
    const T = tipoTrasporto();
    if (!T) throw new Error("browser non supportato: usa Chrome");
    const d = auto ? await T.giaAutorizzato() : await T.scegli();
    if (!d) return false;
    const t = new T(d);
    await t.open();
    this.t = t;
    t.readLoop(u8 => this._dati(u8)).catch(() => this.disconnetti());
    // DTR attivo: la UNO si riavvia e lo sketch stampa READY <id>
    await t.setSignals(false, false);
    await sleep(100);
    await t.setSignals(true, true);
    this.dispatchEvent(new Event("stato"));
    return true;
  }

  async disconnetti() {
    if (!this.t) return;
    const t = this.t; this.t = null;
    await t.close();
    this.dispatchEvent(new Event("stato"));
  }

  _dati(u8) {
    if (this.modo === "binario") {
      for (const b of u8) this.raw.push(b);
      if (this.attesa) { const a = this.attesa; this.attesa = null; a(); }
      return;
    }
    this.riga += dec.decode(u8, { stream: true });
    let i;
    while ((i = this.riga.indexOf("\n")) >= 0) {
      const l = this.riga.slice(0, i).replace(/\r$/, "");
      this.riga = this.riga.slice(i + 1);
      if (l) this.dispatchEvent(new CustomEvent("riga", { detail: l }));
    }
  }

  async inviaRiga(s) {
    if (!this.t || this.modo !== "testo") return;
    this.dispatchEvent(new CustomEvent("inviata", { detail: s }));
    await this.t.write(enc.encode(s + "\n"));
  }

  // ---- primitive binarie per il programmatore ----
  setModo(m) { this.modo = m; this.raw = []; this.riga = ""; }
  svuota() { this.raw = []; }
  scrivi(u8) { return this.t.write(u8); }
  segnali(dtr, rts) { return this.t.setSignals(dtr, rts); }
  async leggi(n, timeout = 1000) {
    const fine = Date.now() + timeout;
    while (this.raw.length < n) {
      const resto = fine - Date.now();
      if (resto <= 0) throw new Error("timeout");
      await Promise.race([new Promise(r => (this.attesa = r)), sleep(resto)]);
    }
    return this.raw.splice(0, n);
  }
}
