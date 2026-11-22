// Programmazione della UNO dal browser: bootloader Optiboot, protocollo STK500v1
// (lo stesso che usa l'IDE Arduino tramite avrdude).
import { sleep } from "./link.js";

const OK = 0x14, INSYNC_END = 0x10, EOP = 0x20;
const PAGINA = 128;               // ATmega328P: pagine da 128 byte
const MAX_FLASH = 32256;          // 32 KB meno 512 byte di bootloader
const FIRMA_328P = [0x1e, 0x95, 0x0f];

export function leggiHex(testo) {
  const mem = new Uint8Array(MAX_FLASH).fill(0xff);
  let base = 0, fine = 0;
  for (const raw of testo.split(/\r?\n/)) {
    const r = raw.trim();
    if (!r) continue;
    if (r[0] !== ":") throw new Error("file .hex non valido");
    const b = r.slice(1).match(/../g).map(h => parseInt(h, 16));
    const len = b[0], addr = (b[1] << 8) | b[2], tipo = b[3];
    const somma = b.reduce((s, x) => s + x, 0) & 0xff;
    if (somma !== 0) throw new Error("checksum .hex errato");
    if (tipo === 0x00) {
      const a = base + addr;
      if (a + len > MAX_FLASH) throw new Error("programma troppo grande per la UNO");
      for (let i = 0; i < len; i++) mem[a + i] = b[4 + i];
      fine = Math.max(fine, a + len);
    } else if (tipo === 0x01) break;
    else if (tipo === 0x02) base = ((b[4] << 8) | b[5]) << 4;
    else if (tipo === 0x04) base = ((b[4] << 8) | b[5]) << 16;
  }
  return mem.slice(0, Math.ceil(fine / PAGINA) * PAGINA);
}

async function cmd(link, bytes, nRisposta, timeout = 1000) {
  await link.scrivi(Uint8Array.from(bytes));
  const r = await link.leggi(nRisposta, timeout);
  if (r[0] !== OK || r[r.length - 1] !== INSYNC_END) throw new Error("risposta inattesa dal bootloader");
  return r.slice(1, -1);
}

async function sincronizza(link) {
  // reset: DTR/RTS giù e su, come fa avrdude
  await link.segnali(false, false);
  await sleep(250);
  await link.segnali(true, true);
  await sleep(50);
  for (let i = 0; i < 12; i++) {
    link.svuota();
    await link.scrivi(Uint8Array.of(0x30, EOP));
    try {
      const r = await link.leggi(2, 250);
      if (r[0] === OK && r[1] === INSYNC_END) {
        await sleep(30);
        link.svuota();
        return;
      }
    } catch {}
  }
  throw new Error("il bootloader non risponde (premi RESET sulla scheda e riprova)");
}

// progresso(frazione 0..1, fase)
export async function programma(link, immagine, progresso = () => {}) {
  link.setModo("binario");
  try {
    progresso(0, "Riavvio della scheda…");
    await sincronizza(link);

    const firma = await cmd(link, [0x75, EOP], 5);
    if (firma.some((x, i) => x !== FIRMA_328P[i])) {
      throw new Error("microcontrollore non riconosciuto (" + firma.map(x => x.toString(16)).join(" ") + ")");
    }

    const pagine = immagine.length / PAGINA;
    const indirizzo = a => [0x55, (a >> 1) & 0xff, (a >> 9) & 0xff, EOP];

    for (let p = 0; p < pagine; p++) {
      const a = p * PAGINA;
      await cmd(link, indirizzo(a), 2);
      await cmd(link, [0x64, 0x00, PAGINA, 0x46, ...immagine.subarray(a, a + PAGINA), EOP], 2, 2000);
      progresso((p + 1) / pagine * 0.5, "Scrittura…");
    }
    for (let p = 0; p < pagine; p++) {
      const a = p * PAGINA;
      await cmd(link, indirizzo(a), 2);
      const letti = await cmd(link, [0x74, 0x00, PAGINA, 0x46, EOP], PAGINA + 2, 2000);
      for (let i = 0; i < PAGINA; i++) {
        if (letti[i] !== immagine[a + i]) throw new Error(`verifica fallita all'indirizzo ${a + i}`);
      }
      progresso(0.5 + (p + 1) / pagine * 0.5, "Verifica…");
    }
    await cmd(link, [0x51, EOP], 2);   // esce dal bootloader: parte il nuovo programma
  } finally {
    link.setModo("testo");
  }
}
