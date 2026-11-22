import { Link, browserSupportato, sleep } from "./link.js";
import { leggiHex, programma } from "./flasher.js";
import { PROGETTI, LIVELLI, h } from "./progetti.js";

const link = new Link();
const stato = {
  caricato: null,     // id del firmware presente sulla scheda, "?" se sconosciuto
  inCarica: null,     // id del progetto che si sta caricando
  progresso: 0,
  fase: "",
  errore: "",
};
const $app = document.getElementById("app");
const $chip = document.getElementById("chip");
const $btn = document.getElementById("btnConnetti");
const $log = document.getElementById("log");
let smonta = null;          // pulizia della pagina di comando aperta
let ascoltatori = [];       // callback riga della pagina aperta

const trova = id => PROGETTI.find(p => p.id === id);

function log(s) {
  $log.textContent += s + "\n";
  if ($log.textContent.length > 20000) $log.textContent = $log.textContent.slice(-15000);
  $log.scrollTop = $log.scrollHeight;
}

// ------------------------------------------------------------------ collegamento
link.addEventListener("riga", e => {
  const l = e.detail;
  if (!l.startsWith("V ")) log("← " + l);
  const m = l.match(/^(READY|ID)\s+(\S+)/);
  if (m) { cambiaCaricato(m[2]); }
  else if (l === "READY") cambiaCaricato("?");
  ascoltatori.forEach(f => f(l));
});
link.addEventListener("inviata", e => log("→ " + e.detail));
link.addEventListener("stato", () => {
  if (!link.connesso) stato.caricato = null;
  aggiornaBarra();
  disegna();
});

function cambiaCaricato(id) {
  if (stato.caricato === id) return;
  stato.caricato = id;
  aggiornaBarra();
  if (!stato.inCarica) disegna();
}

async function connetti(auto = false) {
  try {
    const ok = await link.connetti(auto);
    if (!ok) return;
    log("Collegato (" + link.t.nome + ")");
    stato.caricato = null;
    aggiornaBarra();
    // lo sketch si presenta da solo dopo il reset; se tace glielo chiediamo
    await sleep(2500);
    if (link.connesso && !stato.caricato) await link.inviaRiga("ID?");
    await sleep(800);
    if (link.connesso && !stato.caricato) cambiaCaricato("?");
  } catch (e) {
    if (!auto && e.name !== "NotFoundError") alert("Collegamento non riuscito: " + e.message);
  }
}

function aggiornaBarra() {
  if (!browserSupportato()) {
    $chip.textContent = "Browser non supportato";
    $chip.className = "chip err";
    $btn.hidden = true;
    return;
  }
  if (!link.connesso) {
    $chip.textContent = "Non collegato";
    $chip.className = "chip";
    $btn.textContent = "Collega";
    $btn.className = "primario";
  } else {
    const p = trova(stato.caricato);
    $chip.textContent = stato.caricato === null ? "Collegato…" :
      p ? "Sulla scheda: " + p.nome : "Programma sconosciuto";
    $chip.className = "chip on";
    $btn.textContent = "Stacca";
    $btn.className = "";
  }
}
$btn.onclick = () => (link.connesso ? link.disconnetti() : connetti());

// ------------------------------------------------------------------ caricamento
async function carica(id) {
  if (!link.connesso) { await connetti(); if (!link.connesso) return; }
  const p = trova(id);
  stato.inCarica = id; stato.progresso = 0; stato.fase = "Scarico il firmware…"; stato.errore = "";
  disegna();
  try {
    const r = await fetch(`firmware/${id}.hex`, { cache: "no-cache" });
    if (!r.ok) throw new Error("firmware non trovato sul server");
    const img = leggiHex(await r.text());
    log(`Carico «${p.nome}» (${img.length} byte)…`);
    const t0 = performance.now();
    await programma(link, img, (f, fase) => {
      stato.progresso = f; stato.fase = fase;
      aggiornaProgresso();
    });
    log(`Caricato in ${((performance.now() - t0) / 1000).toFixed(1)} s`);
    stato.caricato = null;
    stato.fase = "Avvio del programma…";
    aggiornaProgresso();
    // attende READY <id> dal nuovo programma
    for (let i = 0; i < 30 && stato.caricato !== id; i++) await sleep(100);
    if (stato.caricato !== id) { await link.inviaRiga("ID?"); await sleep(500); }
    stato.inCarica = null;
    if (location.hash !== "#/p/" + id) location.hash = "#/p/" + id;
    else disegna();
  } catch (e) {
    log("Errore: " + e.message);
    stato.errore = e.message;
    stato.inCarica = null;
    disegna();
  }
}

function aggiornaProgresso() {
  const b = document.querySelector(".progresso > div");
  const f = document.querySelector(".fase");
  if (b) b.style.width = Math.round(stato.progresso * 100) + "%";
  if (f) f.textContent = stato.fase + " " + Math.round(stato.progresso * 100) + "%";
}

// ------------------------------------------------------------------ viste
function schedaProgetto(p) {
  const sopra = stato.caricato === p.id;
  const inCorso = stato.inCarica === p.id;
  const occupato = !!stato.inCarica;
  return h("article", { class: "card progetto" + (sopra ? " attivo" : "") },
    h("div", { class: "testa" },
      h("span", { class: "icona" }, p.icona),
      h("div", {},
        h("h2", {}, h("span", { class: "num" }, p.n), p.nome, sopra ? h("span", { class: "badge" }, "caricato") : null),
        h("p", {}, p.descr))),
    h("details", {},
      h("summary", {}, "Collegamenti"),
      h("ul", {}, ...p.collegamenti.map(c => h("li", {}, c))),
      h("a", { class: "guida", href: `guide/${p.id}.pdf`, target: "_blank" }, "📄 Guida PDF con disegni")),
    inCorso
      ? h("div", {}, h("div", { class: "progresso" }, h("div", {})), h("p", { class: "fase" }, stato.fase))
      : h("div", { class: "riga" },
          h("button", { class: sopra ? "" : "primario", disabled: occupato || !browserSupportato(),
            onclick: () => carica(p.id) }, sopra ? "Ricarica" : "Carica sulla scheda"),
          h("button", { class: sopra ? "primario" : "", disabled: occupato,
            onclick: () => (location.hash = "#/p/" + p.id) }, "Comandi")));
}

function vistaHome() {
  const figli = [];
  if (!browserSupportato()) {
    figli.push(h("div", { class: "card avviso" },
      "Questo browser non può parlare con la scheda. Apri la pagina con Chrome su Android, oppure Chrome/Edge su PC."));
  } else if (!link.connesso) {
    figli.push(h("div", { class: "card avviso" },
      "Collega la UNO al telefono (hub o adattatore OTG) e premi «Collega» in alto."));
  }
  if (stato.errore) figli.push(h("div", { class: "card errore" }, "Caricamento non riuscito: " + stato.errore));
  const p = trova(stato.caricato);
  if (p && !stato.inCarica) {
    figli.push(h("button", { class: "primario largo", onclick: () => (location.hash = "#/p/" + p.id) },
      `Apri i comandi di «${p.nome}»`));
  }
  let liv = 0;
  for (const p of PROGETTI) {
    if (p.livello !== liv) { liv = p.livello; figli.push(h("h3", { class: "livello" }, LIVELLI[liv])); }
    figli.push(schedaProgetto(p));
  }
  return figli;
}

function vistaProgetto(p) {
  const corpo = h("div", { class: "card" });
  const figli = [
    h("button", { class: "indietro", onclick: () => (location.hash = "#/") }, "‹ Progetti"),
    h("h1", {}, p.icona + " " + p.nome),
  ];
  if (!link.connesso) {
    figli.push(h("div", { class: "card avviso" }, "Scheda non collegata: premi «Collega» in alto."));
  } else if (stato.caricato && stato.caricato !== p.id) {
    figli.push(h("div", { class: "card avviso" },
      h("p", {}, "Sulla scheda c'è un altro programma: questi comandi non funzioneranno."),
      h("button", { class: "primario", onclick: () => { location.hash = "#/"; carica(p.id); } },
        "Carica «" + p.nome + "»")));
  }
  figli.push(corpo,
    h("details", { class: "card" }, h("summary", {}, "Collegamenti"),
      h("ul", {}, ...p.collegamenti.map(c => h("li", {}, c))),
      h("a", { class: "guida", href: `guide/${p.id}.pdf`, target: "_blank" }, "📄 Guida PDF con disegni")));
  const api = {
    invia: s => link.inviaRiga(s).catch(e => log("Errore invio: " + e.message)),
    onRiga: f => ascoltatori.push(f),
  };
  const r = p.monta(corpo, api);
  smonta = typeof r === "function" ? r : null;
  return figli;
}

function disegna() {
  if (smonta) { try { smonta(); } catch {} smonta = null; }
  ascoltatori = [];
  const m = location.hash.match(/^#\/p\/(\w+)/);
  const p = m && trova(m[1]);
  $app.replaceChildren(...(p && !stato.inCarica ? vistaProgetto(p) : vistaHome()));
}

window.addEventListener("hashchange", disegna);
navigator.usb?.addEventListener("disconnect", () => { log("Cavo scollegato"); link.disconnetti(); });

aggiornaBarra();
disegna();
// se la scheda è già stata autorizzata in passato, si ricollega da sola
if (browserSupportato()) connetti(true);
