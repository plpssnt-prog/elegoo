// Elenco dei progetti di test. Per aggiungerne uno:
//  1. crea sketches/<id>/<id>.ino (deve stampare "READY <id>" all'avvio e rispondere a "ID?")
//  2. aggiungi qui un oggetto con lo stesso id e la sua pagina di comando (monta)
// Il file public/firmware/<id>.hex lo genera la GitHub Action.

export function h(tag, attr = {}, ...figli) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attr)) {
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (v !== false && v != null) el.setAttribute(k, v === true ? "" : v);
  }
  for (const f of figli.flat()) if (f != null) el.append(f);
  return el;
}

// Invio con limitazione: durante un trascinamento parte al massimo un comando ogni `ms`
export function limitato(fn, ms = 40) {
  let occupato = false, prossimo = null;
  const go = async v => {
    if (occupato) { prossimo = v; return; }
    occupato = true;
    try { await fn(v); } catch {}
    setTimeout(() => {
      occupato = false;
      if (prossimo !== null) { const p = prossimo; prossimo = null; go(p); }
    }, ms);
  };
  return go;
}

const slider = (min, max, val, oninput, step = 1) =>
  h("input", { type: "range", min, max, step, value: val, oninput: e => oninput(+e.target.value) });

export const PROGETTI = [
  // ---------------------------------------------------------------- BLINK
  {
    id: "blink",
    n: 1, livello: 1,
    icona: "💡",
    nome: "LED integrato",
    descr: "Accende e fa lampeggiare il LED «L» sulla scheda. Nessun collegamento: ottimo primo test.",
    collegamenti: ["Nessuno: si usa il LED arancione «L» vicino al pin 13."],
    monta(el, api) {
      const valore = h("div", { class: "grande" }, "500 ms");
      const invia = limitato(v => api.invia("B" + v));
      const s = slider(100, 2000, 500, v => { valore.textContent = v + " ms"; invia(v); }, 50);
      el.append(
        h("div", { class: "griglia3" },
          h("button", { onclick: () => api.invia("L1") }, "Acceso"),
          h("button", { onclick: () => api.invia("L0") }, "Spento"),
          h("button", { class: "primario", onclick: () => api.invia("B" + s.value) }, "Lampeggia")),
        h("p", { class: "etichetta" }, "Velocità del lampeggio (durata di un ciclo)"),
        valore, s);
    },
  },

  // ---------------------------------------------------------------- SERVO
  {
    id: "servo",
    n: 11, livello: 3,
    icona: "🦾",
    nome: "Servo + sensore distanza",
    descr: "Servo SG90 e sensore a ultrasuoni HC-SR04: comando manuale, radar e modalità «segui la mano».",
    collegamenti: [
      "UNO 5V → riga + della breadboard, UNO GND → riga –",
      "Servo: rosso → riga +, marrone → riga –, arancione → pin 9",
      "HC-SR04: Vcc → riga +, Gnd → riga –, Trig → pin 12, Echo → pin 11",
      "Per il radar fissa il sensore sul braccio del servo e usa i cavetti maschio-femmina.",
    ],
    monta(el, api) {
      const fmt = cm => (cm < 0 ? "fuori portata" : cm.toFixed(1) + " cm");
      const corpo = h("div", { class: "colonna" });
      const tab = [["Manuale", manuale], ["Radar", radar], ["Segui", segui]];
      const bottoni = tab.map(([n, f], i) => h("button", { onclick: () => apri(i) }, n));
      el.append(h("div", { class: "schede" }, ...bottoni), corpo);
      let gestore = null;
      api.onRiga(l => gestore && gestore(l));

      function apri(i) {
        bottoni.forEach((b, j) => b.classList.toggle("attiva", i === j));
        corpo.replaceChildren();
        gestore = null;
        tab[i][1]();
      }

      function quadrante() {
        const lancetta = h("div", { class: "lancetta" });
        return { el: h("div", { class: "quadrante" }, lancetta, h("div", { class: "perno" })),
                 gira: a => (lancetta.style.transform = `rotate(${a - 90}deg)`) };
      }

      // --- Manuale: slider + distanza in tempo reale
      function manuale() {
        api.invia("M0");
        const q = quadrante();
        const valore = h("div", { class: "grande" }, "90°");
        const dist = h("div", { class: "distanza" }, "–");
        const invia = limitato(v => api.invia("A" + v));
        const imposta = v => { valore.textContent = v + "°"; q.gira(v); s.value = v; invia(v); };
        const s = slider(0, 180, 90, imposta);
        corpo.append(q.el, valore, s,
          h("div", { class: "griglia5" },
            ...[0, 45, 90, 135, 180].map(a => h("button", { onclick: () => imposta(a) }, a + "°"))),
          h("p", { class: "etichetta" }, "Distanza misurata dal sensore"), dist);
        q.gira(90);
        setTimeout(() => { api.invia("A90"); api.invia("S1"); }, 50);
        gestore = l => { if (l.startsWith("D ")) dist.textContent = fmt(parseFloat(l.slice(2))); };
      }

      // --- Radar: il servo spazza da 15° a 165° e disegna gli ostacoli
      function radar() {
        api.invia("S0");
        let portata = 100;
        const punti = new Map();          // angolo -> {cm, t}
        let angoloAttuale = 90;
        const cv = h("canvas", { width: 600, height: 330, class: "grafico" });
        const info = h("p", { class: "etichetta" }, "Avvio…");
        const sel = h("select", { onchange: e => { portata = +e.target.value; disegna(); } },
          ...[[50, "portata 50 cm"], [100, "portata 1 m"], [200, "portata 2 m"]].map(([v, t]) =>
            h("option", { value: v, selected: v === 100 }, t)));
        const pausa = h("button", { onclick: () => {
          const ferma = pausa.textContent === "Pausa";
          api.invia(ferma ? "M0" : "M1");
          pausa.textContent = ferma ? "Riprendi" : "Pausa";
        } }, "Pausa");
        corpo.append(cv, info, h("div", { class: "riga" }, pausa, sel,
          h("button", { onclick: () => { punti.clear(); disegna(); } }, "Pulisci")));
        const ctx = cv.getContext("2d");
        const O = { x: 300, y: 312 }, RAG = 290;
        const pos = (a, r) => {
          const rad = Math.PI - a * Math.PI / 180;
          return [O.x + r * Math.cos(rad), O.y - r * Math.sin(rad)];
        };
        function disegna() {
          ctx.clearRect(0, 0, 600, 330);
          ctx.strokeStyle = "#dfe3ea"; ctx.fillStyle = "#8a90a0"; ctx.lineWidth = 1; ctx.font = "16px system-ui";
          for (let k = 1; k <= 4; k++) {
            ctx.beginPath(); ctx.arc(O.x, O.y, RAG * k / 4, Math.PI, 2 * Math.PI); ctx.stroke();
            ctx.fillText(Math.round(portata * k / 4) + " cm", O.x + 4, O.y - RAG * k / 4 + 16);
          }
          for (const a of [0, 45, 90, 135, 180]) {
            const [x, y] = pos(a, RAG); ctx.beginPath(); ctx.moveTo(O.x, O.y); ctx.lineTo(x, y); ctx.stroke();
          }
          // fascio
          const [fx, fy] = pos(angoloAttuale, RAG);
          ctx.strokeStyle = "rgba(31,111,209,.55)"; ctx.lineWidth = 3;
          ctx.beginPath(); ctx.moveTo(O.x, O.y); ctx.lineTo(fx, fy); ctx.stroke();
          // ostacoli
          const ora = performance.now();
          for (const [a, { cm, t }] of punti) {
            if (cm < 0 || cm > portata) continue;
            const eta = Math.min(1, (ora - t) / 8000);
            const [x, y] = pos(a, cm / portata * RAG);
            ctx.fillStyle = `rgba(212,60,60,${1 - eta * 0.75})`;
            ctx.beginPath(); ctx.arc(x, y, 7, 0, 2 * Math.PI); ctx.fill();
          }
        }
        disegna();
        setTimeout(() => api.invia("M1"), 50);
        gestore = l => {
          const m = l.match(/^R (\d+) (-?[\d.]+)/);
          if (!m) return;
          angoloAttuale = +m[1];
          const cm = parseFloat(m[2]);
          punti.set(angoloAttuale, { cm, t: performance.now() });
          info.textContent = `${angoloAttuale}° · ${fmt(cm)}`;
          disegna();
        };
      }

      // --- Segui: più ti avvicini, più il servo gira
      function segui() {
        api.invia("S0");
        const q = quadrante();
        const valore = h("div", { class: "grande" }, "–");
        const dist = h("div", { class: "distanza" }, "–");
        corpo.append(
          h("p", {}, "Metti la mano davanti al sensore e muovila avanti e indietro tra 5 e 40 cm: il servo la segue."),
          q.el, valore, dist);
        setTimeout(() => api.invia("M2"), 50);
        gestore = l => {
          const m = l.match(/^F (\d+) (-?[\d.]+)/);
          if (!m) return;
          valore.textContent = m[1] + "°"; q.gira(+m[1]);
          dist.textContent = fmt(parseFloat(m[2]));
        };
      }

      apri(0);
      return () => { api.invia("M0"); api.invia("S0"); };
    },
  },

  // ---------------------------------------------------------------- RGB
  {
    id: "rgb",
    n: 5, livello: 1,
    icona: "🌈",
    nome: "LED RGB",
    descr: "Sceglie il colore del LED RGB del kit, con selettore o tre slider.",
    collegamenti: [
      "Piedino più lungo del LED → GND",
      "Rosso → resistenza 220 Ω → pin 6",
      "Verde → resistenza 220 Ω → pin 5",
      "Blu → resistenza 220 Ω → pin 3",
      "Le resistenze da 220 Ω hanno le fasce rosso-rosso-nero(-nero)-marrone.",
    ],
    monta(el, api) {
      let c = [0, 0, 0];
      const anteprima = h("div", { class: "anteprima" });
      const invia = limitato(v => api.invia("C" + v.join(",")));
      const hex = v => "#" + v.map(x => x.toString(16).padStart(2, "0")).join("");
      const ss = ["R", "G", "B"].map((n, i) => slider(0, 255, 0, v => { c[i] = v; aggiorna(); }));
      const picker = h("input", { type: "color", value: "#000000", oninput: e => {
        const x = e.target.value;
        c = [1, 3, 5].map(i => parseInt(x.slice(i, i + 2), 16));
        aggiorna();
      } });
      function aggiorna() {
        c.forEach((v, i) => (ss[i].value = v));
        picker.value = hex(c);
        anteprima.style.background = hex(c);
        invia([...c]);
      }
      const preset = [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 120, 0], [180, 0, 255], [255, 255, 255], [0, 0, 0]];
      el.append(
        h("div", { class: "riga" }, anteprima, picker),
        ...["Rosso", "Verde", "Blu"].map((n, i) => h("label", { class: "etichetta" }, n, ss[i])),
        h("div", { class: "griglia7" },
          ...preset.map(p => h("button", { class: "campione", style: `background:${hex(p)}`,
            "aria-label": hex(p), onclick: () => { c = [...p]; aggiorna(); } }))));
    },
  },

  // ---------------------------------------------------------------- LUCE
  {
    id: "luce",
    n: 7, livello: 2,
    icona: "🔆",
    nome: "Sensore di luce",
    descr: "Legge la fotoresistenza e mostra la luminosità con un grafico in tempo reale.",
    collegamenti: [
      "5V → un piedino della fotoresistenza",
      "Altro piedino della fotoresistenza → A0",
      "A0 → resistenza 10 kΩ → GND",
      "La resistenza da 10 kΩ ha le fasce marrone-nero-arancione (o marrone-nero-nero-rosso).",
    ],
    monta(el, api) {
      const valore = h("div", { class: "grande" }, "–");
      const barra = h("div", { class: "barra-piena" });
      const canvas = h("canvas", { width: 600, height: 220, class: "grafico" });
      const dati = [];
      let min = 1023, max = 0, attivo = true;
      const minmax = h("p", { class: "etichetta" }, "");
      const btn = h("button", { onclick: () => {
        attivo = !attivo;
        api.invia(attivo ? "S1" : "S0");
        btn.textContent = attivo ? "Pausa" : "Riprendi";
      } }, "Pausa");
      const sel = h("select", { onchange: e => api.invia("R" + e.target.value) },
        ...[[50, "veloce"], [100, "normale"], [500, "lento"]].map(([v, t]) =>
          h("option", { value: v, selected: v === 100 }, t)));
      el.append(valore, h("div", { class: "barra" }, barra), minmax, canvas,
        h("div", { class: "riga" }, btn, sel,
          h("button", { onclick: () => { min = 1023; max = 0; dati.length = 0; } }, "Azzera")));

      const ctx = canvas.getContext("2d");
      function disegna() {
        const w = canvas.width, hh = canvas.height;
        ctx.clearRect(0, 0, w, hh);
        ctx.strokeStyle = "#e2e5ea"; ctx.lineWidth = 1;
        for (let i = 1; i < 4; i++) { ctx.beginPath(); ctx.moveTo(0, hh * i / 4); ctx.lineTo(w, hh * i / 4); ctx.stroke(); }
        ctx.strokeStyle = "#e0a800"; ctx.lineWidth = 3; ctx.beginPath();
        dati.forEach((v, i) => {
          const x = i / 199 * w, y = hh - v / 1023 * hh;
          i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
        });
        ctx.stroke();
      }
      api.onRiga(l => {
        if (!l.startsWith("V ")) return;
        const v = parseInt(l.slice(2), 10);
        if (isNaN(v)) return;
        dati.push(v); if (dati.length > 200) dati.shift();
        min = Math.min(min, v); max = Math.max(max, v);
        const pct = Math.round(v / 1023 * 100);
        valore.textContent = pct + "%";
        barra.style.width = pct + "%";
        minmax.textContent = `valore grezzo ${v}  ·  min ${min}  ·  max ${max}`;
        disegna();
      });
      setTimeout(() => api.invia("S1"), 50);
      return () => api.invia("S0");
    },
  },

  // ---------------------------------------------------------------- BUZZER
  {
    id: "buzzer",
    n: 4, livello: 1,
    icona: "🎹",
    nome: "Buzzer",
    descr: "Una piccola tastiera: ogni tasto suona una nota sul buzzer passivo.",
    collegamenti: [
      "Usa il buzzer PASSIVO (senza adesivo, con il circuito verde visibile sotto)",
      "Piedino + del buzzer → pin 8",
      "Altro piedino → GND",
    ],
    monta(el, api) {
      let durata = 300;
      const note = [["Do", 262], ["Re", 294], ["Mi", 330], ["Fa", 349], ["Sol", 392], ["La", 440], ["Si", 494], ["Do", 523]];
      const suona = f => api.invia(`T${f},${durata}`);
      const freq = h("div", { class: "grande" }, "440 Hz");
      const s = slider(100, 2000, 440, v => (freq.textContent = v + " Hz"), 10);
      el.append(
        h("div", { class: "tastiera" },
          ...note.map(([n, f]) => h("button", { class: "tasto", onpointerdown: () => suona(f) }, n))),
        h("label", { class: "etichetta" }, "Durata nota",
          h("select", { onchange: e => (durata = +e.target.value) },
            ...[[150, "breve"], [300, "media"], [800, "lunga"]].map(([v, t]) =>
              h("option", { value: v, selected: v === 300 }, t)))),
        h("p", { class: "etichetta" }, "Frequenza libera"),
        freq, s,
        h("div", { class: "riga" },
          h("button", { class: "primario", onclick: () => suona(+s.value) }, "Suona"),
          h("button", { onclick: () => api.invia("X") }, "Stop")));
    },
  },
  // ================================================================ NUOVI PROGETTI

  // ---------------------------------------------------------------- SEMAFORO
  {
    id: "semaforo",
    n: 2, livello: 1,
    icona: "🚦",
    nome: "Semaforo",
    descr: "Tre LED rosso, giallo e verde: semaforo automatico, lampeggiante o comandato a mano.",
    collegamenti: [
      "Ogni LED: piedino lungo verso il pin, piedino corto → resistenza 220 Ω → riga –",
      "Rosso → pin 12, giallo → pin 11, verde → pin 10",
      "GND della UNO → riga – della breadboard",
    ],
    monta(el, api) {
      const luci = ["#d43c3c", "#e0a800", "#16a065"].map(c => h("div", { class: "lampada", "data-c": c }));
      const accendi = (i, on) => { luci[i].style.background = on ? luci[i].dataset.c : ""; luci[i].style.color = luci[i].dataset.c; luci[i].classList.toggle("on", on); };
      let stato = [0, 0, 0];
      luci.forEach((l, i) => l.addEventListener("click", () => {
        stato[i] = stato[i] ? 0 : 1; api.invia("L" + stato.join(""));
      }));
      const modi = [["Manuale", "M0"], ["Automatico", "M1"], ["Lampeggiante", "M2"]];
      const bott = modi.map(([n, c]) => h("button", { onclick: () => api.invia(c) }, n));
      el.append(h("div", { class: "schede" }, ...bott),
        h("div", { class: "semaforo" }, ...luci),
        h("p", { class: "etichetta centro" }, "In modalità manuale tocca una luce per accenderla o spegnerla."));
      const segnaModo = m => bott.forEach((b, i) => b.classList.toggle("attiva", i === m));
      api.onRiga(l => {
        let m;
        if ((m = l.match(/^S ([01])([01])([01])/))) { stato = [+m[1], +m[2], +m[3]]; stato.forEach((v, i) => accendi(i, v)); }
        else if ((m = l.match(/^M (\d)/))) segnaModo(+m[1]);
      });
      setTimeout(() => api.invia("?"), 50);
    },
  },

  // ---------------------------------------------------------------- PULSANTI
  {
    id: "pulsanti",
    n: 3, livello: 1,
    icona: "🔘",
    nome: "Pulsanti e inclinazione",
    descr: "Due pulsanti e il sensore di inclinazione: l'app mostra in tempo reale cosa premi e conta i clic.",
    collegamenti: [
      "Pulsante A a cavallo della scanalatura: un piedino → pin 2, quello opposto in diagonale → riga –",
      "Pulsante B: un piedino → pin 3, quello opposto in diagonale → riga –",
      "Sensore di inclinazione: un piedino → pin 4, l'altro → riga –",
      "GND della UNO → riga –. Non servono resistenze.",
    ],
    monta(el, api) {
      const spia = (nome) => {
        const s = h("div", { class: "spia" }), cnt = h("span", { class: "conta" }, "0");
        return { el: h("div", { class: "card-spia" }, s, h("b", {}, nome), cnt), s, cnt, n: 0 };
      };
      const A = spia("Pulsante A"), B = spia("Pulsante B"), T = spia("Inclinazione");
      T.cnt.textContent = "";
      const prec = [0, 0, 0];
      el.append(h("div", { class: "griglia3" }, A.el, B.el, T.el),
        h("p", { class: "etichetta centro" }, "Il numero conta le pressioni. Inclina la breadboard per far cambiare il sensore."),
        h("button", { onclick: () => { A.n = B.n = 0; A.cnt.textContent = B.cnt.textContent = "0"; } }, "Azzera conteggi"));
      api.onRiga(l => {
        const m = l.match(/^B ([01])([01])([01])/);
        if (!m) return;
        [A, B, T].forEach((x, i) => {
          const v = +m[i + 1];
          x.s.classList.toggle("on", !!v);
          if (i < 2 && v && !prec[i]) { x.n++; x.cnt.textContent = x.n; }
          prec[i] = v;
        });
        T.cnt.textContent = +m[3] ? "chiuso" : "aperto";
      });
      setTimeout(() => api.invia("?"), 50);
    },
  },

  // ---------------------------------------------------------------- POTENZIOMETRO
  {
    id: "potenziometro",
    n: 6, livello: 2,
    icona: "🎛️",
    nome: "Manopola (potenziometro)",
    descr: "Giri la manopola e la vedi sul telefono; regola la luminosità di un LED, da manopola o da app.",
    collegamenti: [
      "Potenziometro: piedino esterno → riga +, centrale → A0, altro esterno → riga –",
      "LED: piedino lungo → pin 9, corto → resistenza 220 Ω → riga –",
      "5V della UNO → riga +, GND → riga –",
    ],
    monta(el, api) {
      const valore = h("div", { class: "grande" }, "–");
      const barra = h("div", { class: "barra-piena" });
      const led = h("div", { class: "lampada piccola" });
      const s = slider(0, 255, 0, v => { inviaP(v); mostraLed(v); });
      const inviaP = limitato(v => api.invia("P" + v));
      const mostraLed = v => { led.style.background = `rgba(212,60,60,${0.08 + v / 255 * 0.92})`; };
      const bott = [h("button", { onclick: () => api.invia("M0") }, "Comanda la manopola"),
                    h("button", { onclick: () => api.invia("M1") }, "Comanda l'app")];
      el.append(valore, h("div", { class: "barra" }, barra),
        h("div", { class: "schede due" }, ...bott),
        h("div", { class: "riga" }, led, h("div", { style: "flex:1" }, h("p", { class: "etichetta" }, "Luminosità del LED"), s)));
      api.onRiga(l => {
        let m;
        if ((m = l.match(/^V (\d+) (\d+)/))) {
          const v = +m[1];
          valore.textContent = Math.round(v / 1023 * 100) + "%";
          barra.style.width = v / 1023 * 100 + "%";
          if (bott[0].classList.contains("attiva")) { s.value = +m[2]; mostraLed(+m[2]); }
        } else if ((m = l.match(/^M (\d)/))) {
          bott.forEach((b, i) => b.classList.toggle("attiva", i === +m[1]));
          s.disabled = m[1] === "0";
        }
      });
      setTimeout(() => { api.invia("M0"); api.invia("S1"); }, 50);
      return () => api.invia("M0");
    },
  },

  // ---------------------------------------------------------------- METEO
  {
    id: "meteo",
    n: 8, livello: 2,
    icona: "🌡️",
    nome: "Stazione meteo",
    descr: "Temperatura e umidità con il modulo DHT11, e una seconda temperatura dal termistore, con grafico.",
    collegamenti: [
      "DHT11 (cavetti maschio-femmina): S → pin 2, piedino centrale → 5V, – → GND",
      "Termistore: riga + → termistore → A0 → resistenza 10 kΩ → riga –",
      "5V della UNO → riga +, GND → riga –",
    ],
    monta(el, api) {
      const box = (tit, unita) => {
        const v = h("div", { class: "grande" }, "–");
        return { v, el: h("div", { class: "misura" }, h("p", { class: "etichetta" }, tit), v), unita };
      };
      const tD = box("Temperatura (DHT11)", "°C"), uD = box("Umidità", "%"), tT = box("Temperatura (termistore)", "°C");
      const cv = h("canvas", { width: 600, height: 220, class: "grafico" });
      const nota = h("p", { class: "etichetta centro" }, "Aggiornamento ogni 2 secondi");
      el.append(h("div", { class: "griglia2" }, tD.el, uD.el), tT.el, cv,
        h("p", { class: "etichetta legenda" }, h("span", { style: "color:#d43c3c" }, "● DHT11"), "  ", h("span", { style: "color:#1f6fd1" }, "● termistore")),
        nota);
      const dati = [];
      const ctx = cv.getContext("2d");
      function disegna() {
        ctx.clearRect(0, 0, 600, 220);
        const vals = dati.flatMap(d => [d.a, d.b]).filter(v => v > -50);
        if (!vals.length) return;
        let lo = Math.floor(Math.min(...vals) - 1), hi = Math.ceil(Math.max(...vals) + 1);
        const y = v => 200 - (v - lo) / (hi - lo) * 180;
        ctx.fillStyle = "#8a90a0"; ctx.font = "16px system-ui";
        ctx.fillText(hi + "°", 4, 20); ctx.fillText(lo + "°", 4, 210);
        for (const [k, col] of [["a", "#d43c3c"], ["b", "#1f6fd1"]]) {
          ctx.strokeStyle = col; ctx.lineWidth = 3; ctx.beginPath();
          let primo = true;
          dati.forEach((d, i) => {
            if (d[k] <= -50) return;
            const x = 40 + i / 89 * 550;
            primo ? ctx.moveTo(x, y(d[k])) : ctx.lineTo(x, y(d[k])); primo = false;
          });
          ctx.stroke();
        }
      }
      api.onRiga(l => {
        const m = l.match(/^T (-?\d+) (-?\d+) (-?[\d.]+)/);
        if (!m) return;
        const [t, u, tt] = [+m[1], +m[2], +m[3]];
        tD.v.textContent = t > -50 ? t + " °C" : "errore";
        uD.v.textContent = u > -50 ? u + " %" : "errore";
        tT.v.textContent = tt > -50 ? tt.toFixed(1) + " °C" : "errore";
        nota.textContent = t > -50 ? "Aggiornamento ogni 2 secondi" : "Il DHT11 non risponde: controlla i 3 fili del modulo.";
        dati.push({ a: t, b: tt }); if (dati.length > 90) dati.shift();
        disegna();
      });
      setTimeout(() => api.invia("?"), 50);
    },
  },

  // ---------------------------------------------------------------- JOYSTICK
  {
    id: "joystick",
    n: 9, livello: 2,
    icona: "🕹️",
    nome: "Joystick",
    descr: "Muovi il joystick e il pallino sul telefono lo segue; premilo per «sparare».",
    collegamenti: [
      "Cavetti maschio-femmina, niente breadboard:",
      "GND → GND, +5V → 5V, VRx → A0, VRy → A1, SW → pin 2",
    ],
    monta(el, api) {
      const punto = h("div", { class: "punto" });
      const pad = h("div", { class: "pad" }, h("div", { class: "croce-x" }), h("div", { class: "croce-y" }), punto);
      const info = h("p", { class: "etichetta centro" }, "–");
      const tasto = h("div", { class: "spia" });
      let colpi = 0;
      const nColpi = h("b", {}, "0");
      el.append(pad, info, h("div", { class: "riga centro" }, tasto, h("span", {}, "Pulsante premuto · colpi: "), nColpi));
      let prima = 0;
      api.onRiga(l => {
        const m = l.match(/^J (\d+) (\d+) ([01])/);
        if (!m) return;
        const x = +m[1] / 1023, y = +m[2] / 1023, b = +m[3];
        punto.style.left = x * 100 + "%"; punto.style.top = y * 100 + "%";
        punto.classList.toggle("premuto", !!b);
        tasto.classList.toggle("on", !!b);
        if (b && !prima) nColpi.textContent = ++colpi;
        prima = b;
        info.textContent = `X ${m[1]} · Y ${m[2]}`;
      });
      setTimeout(() => api.invia("?"), 50);
    },
  },

  // ---------------------------------------------------------------- ALLARME
  {
    id: "allarme",
    n: 10, livello: 2,
    icona: "🚨",
    nome: "Allarme antifurto",
    descr: "Attivi l'allarme dal telefono: se qualcuno muove la breadboard suonano sirena e LED.",
    collegamenti: [
      "Sensore di inclinazione: un piedino → pin 2, l'altro → riga –",
      "Buzzer ATTIVO (con adesivo): piedino lungo (+) → pin 8, corto → riga –",
      "LED rosso: piedino lungo → pin 12, corto → resistenza 220 Ω → riga –",
      "GND della UNO → riga –",
    ],
    monta(el, api) {
      const stato = h("div", { class: "stato-allarme" }, "–");
      const reg = h("ul", { class: "registro-eventi" });
      const att = h("button", { class: "primario", onclick: () => api.invia("A1") }, "Attiva");
      const dis = h("button", { onclick: () => api.invia("A0") }, "Disattiva");
      el.append(stato, h("div", { class: "riga" }, att, dis),
        h("button", { onclick: () => api.invia("T") }, "Prova la sirena"),
        h("p", { class: "etichetta" }, "Eventi"), reg);
      let prec = null;
      const evento = t => {
        reg.prepend(h("li", {}, new Date().toLocaleTimeString("it-IT") + " · " + t));
        while (reg.children.length > 8) reg.lastChild.remove();
      };
      api.onRiga(l => {
        const m = l.match(/^S ([01]) ([01]) (-?\d)/);
        if (!m) return;
        const [a, al] = [+m[1], +m[2]];
        stato.className = "stato-allarme " + (al ? "allarme" : a ? "attivo" : "");
        stato.textContent = al ? "🚨 ALLARME!" : a ? "🔒 Attivo" : "🔓 Disattivato";
        const k = `${a}${al}`;
        if (prec !== null && k !== prec) evento(al ? "allarme scattato" : a ? "attivato" : "disattivato");
        prec = k;
        if (al && navigator.vibrate) navigator.vibrate([300, 150, 300]);
      });
      setTimeout(() => api.invia("?"), 50);
    },
  },

  // ---------------------------------------------------------------- TELECOMANDO
  {
    id: "telecomando",
    n: 12, livello: 3,
    icona: "📺",
    nome: "Telecomando a infrarossi",
    descr: "Premi i tasti del telecomando del kit: l'app ti mostra quale hai premuto.",
    collegamenti: [
      "Cavetti maschio-femmina, niente breadboard:",
      "Ricevitore IR: G (o –) → GND, R (centrale) → 5V, Y (o S) → pin 11",
    ],
    monta(el, api) {
      const TASTI = [
        ["FFA25D", "⏻"], ["FF629D", "VOL+"], ["FFE21D", "FUNC"],
        ["FF22DD", "⏮"], ["FF02FD", "⏯"], ["FFC23D", "⏭"],
        ["FFE01F", "▼"], ["FFA857", "VOL–"], ["FF906F", "▲"],
        ["FF6897", "0"], ["FF9867", "EQ"], ["FFB04F", "ST/REPT"],
        ["FF30CF", "1"], ["FF18E7", "2"], ["FF7A85", "3"],
        ["FF10EF", "4"], ["FF38C7", "5"], ["FF5AA5", "6"],
        ["FF42BD", "7"], ["FF4AB5", "8"], ["FF52AD", "9"],
      ];
      const btn = new Map(TASTI.map(([c, n]) => [c, h("div", { class: "tasto-ir" + (c === "FFA25D" ? " rosso" : "") }, n)]));
      const ultimo = h("div", { class: "grande" }, "–");
      const cronologia = h("p", { class: "etichetta centro" }, "");
      const storia = [];
      el.append(ultimo, h("div", { class: "telecomando" }, ...btn.values()), cronologia);
      let prec = null;
      const evidenzia = b => { b.classList.add("premuto"); setTimeout(() => b.classList.remove("premuto"), 250); };
      api.onRiga(l => {
        if (l === "R" && prec) { evidenzia(prec); return; }
        const m = l.match(/^K ([0-9A-F]+)/);
        if (!m) return;
        const b = btn.get(m[1]);
        const nome = b ? b.textContent : "sconosciuto (" + m[1] + ")";
        ultimo.textContent = nome;
        if (b) { evidenzia(b); prec = b; }
        storia.unshift(nome); storia.length = Math.min(storia.length, 10);
        cronologia.textContent = "Ultimi: " + storia.join(" · ");
      });
    },
  },

  // ---------------------------------------------------------------- REGISTRO 74HC595
  {
    id: "registro",
    n: 13, livello: 3,
    icona: "🎚️",
    nome: "8 LED con il 74HC595",
    descr: "Il chip 74HC595 comanda 8 LED usando solo 3 pin: accendili uno per uno o scegli un gioco di luci.",
    collegamenti: [
      "Chip 74HC595 a cavallo della scanalatura, tacca a sinistra",
      "16 VCC e 10 MR → riga +, 8 GND e 13 OE → riga –",
      "14 DS → pin 12, 12 latch → pin 11, 11 clock → pin 9",
      "Uscite Q0 (piedino 15) e Q1…Q7 (piedini 1…7) → piedino lungo dei LED; piedino corto → resistenza 220 Ω → riga –",
      "Unisci le righe + e – in alto con quelle in basso; 5V della UNO → riga +, GND → riga –",
    ],
    monta(el, api) {
      let valore = 0;
      const leds = Array.from({ length: 8 }, (_, i) => h("button", { class: "led8", onclick: () => api.invia("W" + (valore ^ (1 << i))) }, "Q" + i));
      const giochi = [["Fermo", 0], ["Supercar", 1], ["Contatore", 2], ["Casuale", 3], ["Riempi", 4]];
      const bott = giochi.map(([n, g]) => h("button", { onclick: () => api.invia("P" + g) }, n));
      const vel = slider(30, 600, 120, v => inviaV(630 - v), 10);
      const inviaV = limitato(v => api.invia("V" + v), 80);
      vel.value = 510;
      el.append(h("div", { class: "ledbar" }, ...leds),
        h("p", { class: "etichetta centro" }, "Tocca un LED per accenderlo o spegnerlo"),
        h("div", { class: "griglia5" }, ...bott),
        h("p", { class: "etichetta" }, "Velocità"), vel,
        h("div", { class: "riga" }, h("button", { onclick: () => api.invia("W255") }, "Tutti accesi"), h("button", { onclick: () => api.invia("W0") }, "Tutti spenti")));
      api.onRiga(l => {
        let m;
        if ((m = l.match(/^S (\d+)/))) { valore = +m[1]; leds.forEach((b, i) => b.classList.toggle("on", !!(valore & (1 << i)))); }
        else if ((m = l.match(/^P (\d)/))) bott.forEach((b, i) => b.classList.toggle("attiva", i === +m[1]));
      });
      setTimeout(() => api.invia("?"), 50);
    },
  },

  // ---------------------------------------------------------------- 7 SEGMENTI
  {
    id: "settesegmenti",
    n: 14, livello: 3,
    icona: "8️⃣",
    nome: "Display a 7 segmenti",
    descr: "Una cifra luminosa comandata dal 74HC595: numeri, conto alla rovescia e lancio del dado.",
    collegamenti: [
      "Chip 74HC595 come nel progetto «8 LED»: 16 e 10 → +, 8 e 13 → –, 14 → pin 12, 12 → pin 11, 11 → pin 9",
      "Uscite del chip → resistenza 220 Ω → segmento: Q0→a, Q1→b, Q2→c, Q3→d, Q4→e, Q5→f, Q6→g, Q7→punto",
      "Display (punto in basso a destra): piedini centrali in alto e in basso (comune) → riga –",
    ],
    monta(el, api) {
      const SEG = { "0": 0x3f, "1": 0x06, "2": 0x5b, "3": 0x4f, "4": 0x66, "5": 0x6d, "6": 0x7d, "7": 0x07, "8": 0x7f, "9": 0x6f,
        A: 0x77, B: 0x7c, C: 0x39, D: 0x5e, E: 0x79, F: 0x71, "-": 0x40, " ": 0 };
      const ns = "http://www.w3.org/2000/svg";
      const svg = document.createElementNS(ns, "svg");
      svg.setAttribute("viewBox", "0 0 120 200"); svg.setAttribute("class", "display7");
      const forme = [[20, 10, 80, 14], [96, 20, 14, 74], [96, 106, 14, 74], [20, 176, 80, 14], [10, 106, 14, 74], [10, 20, 14, 74], [20, 93, 80, 14]];
      const segs = forme.map(([x, y, w, hh]) => {
        const r = document.createElementNS(ns, "rect");
        Object.entries({ x, y, width: w, height: hh, rx: 6 }).forEach(([k, v]) => r.setAttribute(k, v));
        svg.append(r); return r;
      });
      const dp = document.createElementNS(ns, "circle");
      [["cx", 112], ["cy", 190], ["r", 7]].forEach(([k, v]) => dp.setAttribute(k, v)); svg.append(dp);
      let punto = false;
      const tastiera = "1234567890ABCDEF-".split("").map(c => h("button", { onclick: () => api.invia("D" + c) }, c));
      el.append(svg,
        h("div", { class: "griglia6" }, ...tastiera),
        h("div", { class: "riga" },
          h("button", { onclick: () => { punto = !punto; api.invia("." + (punto ? 1 : 0)); } }, "Punto"),
          h("button", { onclick: () => api.invia("E") }, "Spegni")),
        h("div", { class: "riga" },
          h("button", { class: "primario", onclick: () => api.invia("R") }, "🎲 Lancia il dado"),
          h("button", { class: "primario", onclick: () => api.invia("C9") }, "⏱ Conto alla rovescia")));
      api.onRiga(l => {
        const m = l.match(/^S (.)/);
        if (!m) return;
        const v = SEG[m[1]] ?? 0;
        segs.forEach((s, i) => s.classList.toggle("on", !!(v & (1 << i))));
        dp.classList.toggle("on", punto);
      });
      setTimeout(() => api.invia("D-"), 50);
    },
  },

  // ---------------------------------------------------------------- LCD
  {
    id: "lcd",
    n: 15, livello: 3,
    icona: "📟",
    nome: "Display LCD",
    descr: "Scrivi dal telefono due righe di testo sul display LCD 16×2, oppure mostra l'ora.",
    collegamenti: [
      "Righe a-e verso di te. Display con i piedini nella riga e, colonne 12-27: K (16) in colonna 12, VSS (1) in colonna 27",
      "I fili nelle righe a-d, dalla stessa parte della scanalatura dei piedini",
      "VSS, RW, K → riga –; VDD → riga +; A → resistenza 220 Ω → riga +",
      "V0 → centrale del potenziometro (colonne 3-5-7, esterni a + e –)",
      "RS → pin 7, E → pin 8, D4 → pin 9, D5 → pin 10, D6 → pin 11, D7 → pin 12",
      "Se non vedi niente gira il potenziometro: regola il contrasto.",
    ],
    monta(el, api) {
      const norm = t => t.normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^\x20-\x7e]/g, "?").slice(0, 16);
      const r1 = h("input", { class: "testo", maxlength: 16, value: "Ciao dal Pixel!", placeholder: "Riga 1" });
      const r2 = h("input", { class: "testo", maxlength: 16, value: "UNO Lab", placeholder: "Riga 2" });
      const anteprima = h("div", { class: "lcdbox" }, h("div", {}, ""), h("div", {}, ""));
      let orologio = null;
      const mostra = (a, b) => {
        anteprima.children[0].textContent = norm(a).padEnd(16, " ");
        anteprima.children[1].textContent = norm(b).padEnd(16, " ");
      };
      const invia = () => {
        stopOra();
        api.invia("1" + norm(r1.value)); api.invia("2" + norm(r2.value));
        mostra(r1.value, r2.value);
      };
      const stopOra = () => { if (orologio) { clearInterval(orologio); orologio = null; } };
      const ora = () => {
        stopOra();
        const tick = () => {
          const d = new Date();
          const a = d.toLocaleDateString("it-IT", { weekday: "short", day: "2-digit", month: "short" });
          const b = d.toLocaleTimeString("it-IT");
          api.invia("1" + norm(a)); api.invia("2" + norm(b)); mostra(a, b);
        };
        tick(); orologio = setInterval(tick, 1000);
      };
      el.append(anteprima, r1, r2,
        h("button", { class: "primario", onclick: invia }, "Scrivi sul display"),
        h("div", { class: "riga" },
          h("button", { onclick: ora }, "🕒 Mostra l'ora"),
          h("button", { onclick: () => { stopOra(); api.invia("X"); mostra("", ""); } }, "Pulisci")),
        h("p", { class: "etichetta" }, "Massimo 16 caratteri per riga. Le lettere accentate vengono scritte senza accento."));
      mostra("UNO Lab", "pronto!");
      return stopOra;
    },
  },

  // ---------------------------------------------------------------- VENTILATORE
  {
    id: "ventilatore",
    n: 16, livello: 4,
    icona: "🌀",
    nome: "Ventilatore",
    descr: "Il motorino con l'elica, comandato dal chip L293D: velocità e senso di rotazione dal telefono.",
    collegamenti: [
      "Modulo di alimentazione sulla breadboard (ponticelli su 5V) con la batteria 9V",
      "L293D a cavallo della scanalatura, tacca a sinistra",
      "1 → pin 5, 2 → pin 3, 7 → pin 4; 3 e 6 → i due fili del motore",
      "4, 5, 12, 13 → riga –; 16 e 8 → riga +; GND della UNO → riga –",
      "NON collegare il 5V della UNO alla riga +.",
    ],
    monta(el, api) {
      const elica = h("div", { class: "elica" }, "✣");
      const valore = h("div", { class: "grande" }, "0%");
      const invia = limitato(v => api.invia("V" + v), 80);
      const s = slider(-100, 100, 0, v => { valore.textContent = v + "%"; invia(v); }, 5);
      let vel = 0, ang = 0, raf;
      const gira = () => { ang += vel * 0.25; elica.style.transform = `rotate(${ang}deg)`; raf = requestAnimationFrame(gira); };
      gira();
      el.append(elica, valore, s,
        h("div", { class: "riga" },
          h("button", { onclick: () => api.invia("V-60") }, "⟲ Indietro"),
          h("button", { class: "primario", onclick: () => api.invia("S") }, "■ Stop"),
          h("button", { onclick: () => api.invia("V60") }, "Avanti ⟳")),
        h("p", { class: "etichetta" }, "Tieni le dita lontane dall'elica. Sotto il 20% circa il motore può non girare."));
      api.onRiga(l => {
        const m = l.match(/^V (-?\d+)/);
        if (!m) return;
        vel = +m[1]; s.value = vel; valore.textContent = vel + "%";
      });
      setTimeout(() => api.invia("?"), 50);
      return () => { cancelAnimationFrame(raf); api.invia("S"); };
    },
  },

  // ---------------------------------------------------------------- PASSO-PASSO
  {
    id: "passo",
    n: 17, livello: 4,
    icona: "⚙️",
    nome: "Motore passo-passo",
    descr: "Il motore 28BYJ-48 con il driver ULN2003: lo porti esattamente all'angolo che vuoi.",
    collegamenti: [
      "Modulo di alimentazione sulla breadboard (ponticelli su 5V) con la batteria 9V",
      "Driver ULN2003 (cavetti maschio-femmina): IN1 → pin 8, IN2 → pin 9, IN3 → pin 10, IN4 → pin 11",
      "+ del driver → riga +, – del driver → riga –; GND della UNO → riga –",
      "Connettore bianco del motore nella presa del driver",
    ],
    monta(el, api) {
      const cv = h("canvas", { width: 300, height: 300, class: "quadrante-tondo" });
      const valore = h("div", { class: "grande" }, "0°");
      const ctx = cv.getContext("2d");
      let pos = 0, target = null;
      function disegna() {
        ctx.clearRect(0, 0, 300, 300);
        ctx.strokeStyle = "#dfe3ea"; ctx.lineWidth = 14; ctx.beginPath(); ctx.arc(150, 150, 120, 0, 2 * Math.PI); ctx.stroke();
        ctx.fillStyle = "#8a90a0"; ctx.font = "15px system-ui"; ctx.textAlign = "center";
        [[0, "0°"], [90, "90°"], [180, "180°"], [270, "270°"]].forEach(([a, t]) => {
          const r = (a - 90) * Math.PI / 180; ctx.fillText(t, 150 + Math.cos(r) * 95, 155 + Math.sin(r) * 95);
        });
        const lancia = (a, col, w, len) => {
          const r = (a - 90) * Math.PI / 180;
          ctx.strokeStyle = col; ctx.lineWidth = w; ctx.lineCap = "round";
          ctx.beginPath(); ctx.moveTo(150, 150); ctx.lineTo(150 + Math.cos(r) * len, 150 + Math.sin(r) * len); ctx.stroke();
        };
        if (target !== null) lancia(target, "rgba(31,111,209,.3)", 6, 120);
        lancia(pos, "#1f6fd1", 8, 110);
        ctx.fillStyle = "#1b1f27"; ctx.beginPath(); ctx.arc(150, 150, 10, 0, 2 * Math.PI); ctx.fill();
      }
      cv.addEventListener("click", e => {
        const b = cv.getBoundingClientRect();
        const x = (e.clientX - b.left) / b.width * 300 - 150, y = (e.clientY - b.top) / b.height * 300 - 150;
        let a = Math.round(Math.atan2(y, x) * 180 / Math.PI + 90);
        if (a < 0) a += 360;
        target = a; disegna(); api.invia("G" + a);
      });
      const rpm = slider(1, 15, 10, v => inviaV(v));
      const inviaV = limitato(v => api.invia("V" + v), 120);
      el.append(cv, valore,
        h("p", { class: "etichetta centro" }, "Tocca il cerchio per scegliere l'angolo"),
        h("div", { class: "griglia4" },
          ...[["–90°", "R-90"], ["+90°", "R90"], ["Giro intero", "R360"], ["Torna a 0", "G0"]].map(([t, c]) =>
            h("button", { onclick: () => { target = null; api.invia(c); } }, t))),
        h("p", { class: "etichetta" }, "Velocità (giri al minuto)"), rpm,
        h("div", { class: "riga" },
          h("button", { onclick: () => api.invia("Z") }, "Imposta lo zero qui"),
          h("button", { onclick: () => api.invia("X") }, "■ Ferma")));
      api.onRiga(l => {
        const m = l.match(/^(P|FERMO) (-?[\d.]+)/);
        if (!m) return;
        const g = parseFloat(m[2]);
        pos = ((g % 360) + 360) % 360;
        valore.textContent = Math.round(g) + "°";
        if (m[1] === "FERMO") target = null;
        disegna();
      });
      disegna();
      setTimeout(() => api.invia("?"), 50);
      return () => api.invia("X");
    },
  },
  // ================================================================ LIVELLO 5 · AUTONOMI

  // ---------------------------------------------------------------- PARCHEGGIO
  {
    id: "parcheggio",
    n: 18, livello: 5, autonomo: true,
    icona: "🚗",
    nome: "Sensore di parcheggio",
    descr: "Come in auto: più ti avvicini al sensore, più il bip è veloce e il LED passa da verde a rosso.",
    collegamenti: [
      "HC-SR04: Vcc → riga +, Gnd → riga –, Trig → pin 12, Echo → pin 11",
      "Buzzer PASSIVO: + → pin 8, altro → riga –",
      "LED verde → pin 5, giallo → pin 6, rosso → pin 7 (corto → 220 Ω → riga –)",
      "5V della UNO → riga +, GND → riga –",
    ],
    monta(el, api) {
      const dist = h("div", { class: "grande" }, "–");
      const zone = ["Via libera", "Attenzione", "Vicino!", "STOP"];
      const colori = ["#16a065", "#e0a800", "#e06a00", "#d43c3c"];
      const stato = h("div", { class: "stato-allarme" }, "–");
      const barre = colori.map(c => h("div", { class: "arco", style: `--c:${c}` }));
      el.append(h("div", { class: "archi" }, ...barre), dist, stato);
      api.onRiga(l => {
        const m = l.match(/^D (-?[\d.]+) (\d)/);
        if (!m) return;
        const cm = parseFloat(m[1]), z = +m[2];
        dist.textContent = cm < 0 ? "fuori portata" : cm.toFixed(0) + " cm";
        stato.textContent = zone[z];
        stato.style.background = colori[z] + "22"; stato.style.color = colori[z];
        barre.forEach((b, i) => b.classList.toggle("on", i <= z));
      });
    },
  },

  // ---------------------------------------------------------------- TERMOMETRO
  {
    id: "termometro",
    n: 19, livello: 5, autonomo: true,
    icona: "🌡️",
    nome: "Termometro con LCD",
    descr: "Temperatura, umidità, minima e massima sempre visibili sul display LCD, anche a batteria.",
    collegamenti: [
      "Display LCD e potenziometro come nel progetto 15",
      "DHT11: S → pin 2, + → riga +, – → riga –",
    ],
    monta(el, api) {
      const lcd = h("div", { class: "lcdbox" }, h("div", {}, "Termometro       "), h("div", {}, "avvio...         "));
      const t = h("div", { class: "grande" }, "–"), u = h("div", { class: "grande" }, "–");
      const mm = h("p", { class: "etichetta centro" }, "");
      el.append(lcd,
        h("div", { class: "griglia2" },
          h("div", { class: "misura" }, h("p", { class: "etichetta" }, "Temperatura"), t),
          h("div", { class: "misura" }, h("p", { class: "etichetta" }, "Umidità"), u)),
        mm, h("button", { onclick: () => api.invia("Z") }, "Azzera minima e massima"));
      api.onRiga(l => {
        const m = l.match(/^T (-?\d+) (-?\d+) (-?\d+) (-?\d+)/);
        if (!m) return;
        if (+m[1] < -50) { t.textContent = u.textContent = "–"; mm.textContent = "Il DHT11 non risponde: controlla i 3 fili."; return; }
        t.textContent = m[1] + " °C"; u.textContent = m[2] + " %";
        mm.textContent = `minima ${m[3]} °C · massima ${m[4]} °C`;
        lcd.children[0].textContent = `${m[1].padStart(3)}°C  Umid ${m[2].padStart(2)}% `;
        lcd.children[1].textContent = `min ${m[3].padStart(2)}  max ${m[4].padStart(2)}  `;
      });
    },
  },

  // ---------------------------------------------------------------- SIMON
  {
    id: "simon",
    n: 20, livello: 5, autonomo: true,
    icona: "🎮",
    nome: "Gioco Simon",
    descr: "Il gioco della memoria: la UNO accende una sequenza di luci e suoni, tu la ripeti con i pulsanti.",
    collegamenti: [
      "LED rosso → pin 2, verde → pin 3, blu → pin 4, giallo → pin 5 (corto → 220 Ω → riga –)",
      "Pulsanti: rosso → pin 6, verde → pin 7, blu → pin 8, giallo → pin 9 (opposto in diagonale → riga –)",
      "Buzzer PASSIVO: + → pin 10, altro → riga –",
      "GND della UNO → riga –",
    ],
    monta(el, api) {
      const STATI = ["Premi un pulsante per iniziare", "Guarda e ascolta…", "Tocca a te!", "Sbagliato! 😵"];
      const stato = h("div", { class: "stato-allarme" }, "–");
      const liv = h("div", { class: "grande" }, "0"), rec = h("div", { class: "grande" }, "0");
      el.append(stato,
        h("div", { class: "griglia2" },
          h("div", { class: "misura" }, h("p", { class: "etichetta" }, "Livello"), liv),
          h("div", { class: "misura" }, h("p", { class: "etichetta" }, "Record 🏆"), rec)),
        h("p", { class: "etichetta" }, "Il record resta salvato sulla scheda anche quando la spegni."),
        h("button", { onclick: () => { if (confirm("Azzerare il record?")) api.invia("Z"); } }, "Azzera il record"));
      api.onRiga(l => {
        const m = l.match(/^S (\d) (\d+) (\d+)/);
        if (!m) return;
        stato.textContent = STATI[+m[1]];
        stato.className = "stato-allarme" + (m[1] === "2" ? " attivo" : m[1] === "3" ? " allarme" : "");
        liv.textContent = m[2]; rec.textContent = m[3];
      });
    },
  },

  // ---------------------------------------------------------------- DADO
  {
    id: "dado",
    n: 21, livello: 5, autonomo: true,
    icona: "🎲",
    nome: "Dado elettronico",
    descr: "Scuoti la breadboard: il sensore di inclinazione se ne accorge e il display tira un dado da 1 a 6.",
    collegamenti: [
      "74HC595 e display a 7 segmenti come nel progetto 14",
      "Sensore di inclinazione: un piedino → pin 2, l'altro → riga –",
    ],
    monta(el, api) {
      const PUNTI = { 1: [4], 2: [0, 8], 3: [0, 4, 8], 4: [0, 2, 6, 8], 5: [0, 2, 4, 6, 8], 6: [0, 2, 3, 5, 6, 8] };
      const celle = Array.from({ length: 9 }, () => h("div", { class: "pip" }));
      const faccia = h("div", { class: "dado" }, ...celle);
      const info = h("p", { class: "etichetta centro" }, "Scuoti la breadboard tre volte di fila");
      const mostra = n => celle.forEach((c, i) => c.classList.toggle("on", PUNTI[n]?.includes(i)));
      const storia = [];
      const st = h("p", { class: "etichetta centro" }, "");
      el.append(faccia, info, st,
        h("button", { class: "primario", onclick: () => api.invia("R") }, "🎲 Tira dal telefono"),
        h("details", {}, h("summary", {}, "Il display mostra numeri strani o resta spento?"),
          h("p", { class: "etichetta" }, "Alcuni display sono «ad anodo comune»: in quel caso i piedini centrali vanno alla riga + invece che alla –, e scegli qui sotto l'altra modalità."),
          h("div", { class: "riga" },
            h("button", { onclick: () => api.invia("K0") }, "Catodo comune"),
            h("button", { onclick: () => api.invia("K1") }, "Anodo comune"))));
      let anim = null;
      api.onRiga(l => {
        if (l === "L") {
          info.textContent = "Lancio…";
          clearInterval(anim); anim = setInterval(() => mostra(1 + Math.floor(Math.random() * 6)), 80);
          return;
        }
        const m = l.match(/^N (\d)/);
        if (!m) return;
        clearInterval(anim); mostra(+m[1]);
        info.textContent = "È uscito " + m[1];
        storia.unshift(m[1]); storia.length = Math.min(storia.length, 12);
        st.textContent = "Ultimi lanci: " + storia.join(" · ");
      });
      return () => clearInterval(anim);
    },
  },

  // ---------------------------------------------------------------- METRO
  {
    id: "metro",
    n: 22, livello: 5, autonomo: true,
    icona: "📏",
    nome: "Metro portatile",
    descr: "Misura le distanze con gli ultrasuoni e le scrive sul display LCD; un pulsante blocca la misura.",
    collegamenti: [
      "Display LCD e potenziometro come nel progetto 15",
      "HC-SR04: Vcc → riga +, Gnd → riga –, Trig → pin 2, Echo → pin 3",
      "Pulsante «blocca» fuori dalla breadboard, con due cavetti maschio-femmina: un piedino → pin 4, quello opposto in diagonale → riga –",
    ],
    monta(el, api) {
      const lcd = h("div", { class: "lcdbox" }, h("div", {}, "Metro UNO Lab    "), h("div", {}, "                "));
      const dist = h("div", { class: "grande" }, "–");
      const blocca = h("button", { class: "primario", onclick: () => api.invia("B") }, "Blocca la misura");
      el.append(lcd, dist, blocca, h("p", { class: "etichetta" }, "La barra sul display arriva a 2 metri. Il sensore misura bene da 3 cm a circa 3 metri, su superfici piatte."));
      api.onRiga(l => {
        const m = l.match(/^D (-?[\d.]+) ([01])/);
        if (!m) return;
        const cm = parseFloat(m[1]), b = m[2] === "1";
        dist.textContent = cm < 0 ? "fuori portata" : cm.toFixed(1) + " cm";
        blocca.textContent = b ? "Sblocca" : "Blocca la misura";
        const r1 = cm < 0 ? "Fuori portata" : `${cm.toFixed(1).padStart(5)} cm  ${b ? "[STOP]" : ""}`;
        const n = cm < 0 ? 0 : Math.max(0, Math.min(16, Math.round(cm / 200 * 16)));
        lcd.children[0].textContent = r1.padEnd(16);
        lcd.children[1].textContent = "█".repeat(n).padEnd(16);
      });
    },
  },

  // ---------------------------------------------------------------- LAMPADA
  {
    id: "lampada",
    n: 23, livello: 5, autonomo: true,
    icona: "🌙",
    nome: "Lampada notturna",
    descr: "Quando fa buio i LED si accendono piano piano da soli; con la manopola scegli quanto buio deve fare.",
    collegamenti: [
      "Fotoresistenza: riga + → fotoresistenza → A0 → resistenza 10 kΩ → riga –",
      "Potenziometro: esterni → riga + e riga –, centrale → A1",
      "2 LED bianchi → pin 9 e pin 10 (corto → 220 Ω → riga –)",
      "5V della UNO → riga +, GND → riga –",
    ],
    monta(el, api) {
      const luce = h("div", { class: "barra-piena" }), soglia = h("div", { class: "soglia" });
      const lamp = h("div", { class: "lampada grande-l" });
      const testo = h("p", { class: "etichetta centro" }, "–");
      el.append(lamp, testo,
        h("p", { class: "etichetta" }, "Luce nella stanza (la linea è la soglia scelta con la manopola)"),
        h("div", { class: "barra rel" }, luce, soglia),
        h("p", { class: "etichetta" }, "Copri la fotoresistenza con la mano per simulare il buio."));
      api.onRiga(l => {
        const m = l.match(/^L (\d+) (\d+) (\d+)/);
        if (!m) return;
        const [v, s, b] = [+m[1], +m[2], +m[3]];
        luce.style.width = v / 1023 * 100 + "%";
        soglia.style.left = s / 1023 * 100 + "%";
        lamp.style.background = `rgba(255,214,90,${0.08 + b / 255 * 0.92})`;
        lamp.style.boxShadow = b ? `0 0 ${10 + b / 6}px rgba(255,200,60,.8)` : "none";
        testo.textContent = b ? `LED accesi al ${Math.round(b / 255 * 100)}%` : "LED spenti: c'è abbastanza luce";
      });
    },
  },

  // ---------------------------------------------------------------- CRONOMETRO
  {
    id: "cronometro",
    n: 24, livello: 5, autonomo: true,
    icona: "⏱️",
    nome: "Cronometro a 4 cifre",
    descr: "Un cronometro vero sul display a 4 cifre, con i pulsanti avvia/ferma e azzera.",
    collegamenti: [
      "74HC595 come nel progetto 13; uscite → resistenza 1 kΩ → segmenti (Q0 a … Q6 g, Q7 punto)",
      "Display: cifre D1 → pin 2, D2 → pin 3, D3 → pin 4, D4 → pin 5",
      "Pulsante avvia/ferma → pin 6, azzera → pin 7 (opposto in diagonale → riga –)",
    ],
    monta(el, api) {
      const disp = h("div", { class: "cifre4" }, "00.00");
      const corre = h("p", { class: "etichetta centro" }, "–");
      el.append(disp, corre,
        h("div", { class: "riga" },
          h("button", { class: "primario", onclick: () => api.invia("S") }, "Avvia / ferma"),
          h("button", { onclick: () => api.invia("Z") }, "Azzera")),
        h("details", {}, h("summary", {}, "Il display è spento o mostra segni strani?"),
          h("p", { class: "etichetta" }, "Se il tuo display è «ad anodo comune» scegli l'altra modalità qui sotto (resta salvata sulla scheda)."),
          h("div", { class: "riga" },
            h("button", { onclick: () => api.invia("K0") }, "Catodo comune"),
            h("button", { onclick: () => api.invia("K1") }, "Anodo comune"))));
      api.onRiga(l => {
        const m = l.match(/^C (\d+) ([01])/);
        if (!m) return;
        const t = +m[1];
        if (t < 100000) disp.textContent = (t / 1000).toFixed(2).padStart(5, "0");
        else { const s = Math.floor(t / 1000); disp.textContent = String(Math.floor(s / 60) % 100).padStart(2, "0") + "." + String(s % 60).padStart(2, "0"); }
        corre.textContent = m[2] === "1" ? "In corsa" : "Fermo";
      });
    },
  },

  // ---------------------------------------------------------------- SERVO + TELECOMANDO
  {
    id: "servoir",
    n: 25, livello: 5, autonomo: true,
    icona: "🛰️",
    nome: "Servo col telecomando",
    descr: "Muovi il servo con i tasti del telecomando a infrarossi, senza telefono.",
    collegamenti: [
      "5V della UNO → riga +, GND → riga –",
      "Servo: rosso → riga +, marrone → riga –, arancione → pin 9",
      "Ricevitore IR: G → riga –, R → riga +, Y → pin 11",
    ],
    monta(el, api) {
      const lancetta = h("div", { class: "lancetta" });
      const valore = h("div", { class: "grande" }, "–");
      const auto = h("p", { class: "etichetta centro" }, "");
      el.append(h("div", { class: "quadrante" }, lancetta, h("div", { class: "perno" })), valore, auto,
        h("ul", { class: "legenda-tasti" },
          h("li", {}, h("b", {}, "0 … 9"), " angolo da 0° a 180°"),
          h("li", {}, h("b", {}, "⏮ ⏭"), " ±10°"),
          h("li", {}, h("b", {}, "VOL– VOL+"), " ±1°"),
          h("li", {}, h("b", {}, "⏯"), " movimento automatico avanti e indietro"),
          h("li", {}, h("b", {}, "⏻"), " torna al centro")));
      api.onRiga(l => {
        const m = l.match(/^A (\d+) ([01])/);
        if (!m) return;
        valore.textContent = m[1] + "°";
        lancetta.style.transform = `rotate(${+m[1] - 90}deg)`;
        auto.textContent = m[2] === "1" ? "Movimento automatico attivo" : "";
      });
      setTimeout(() => api.invia("?"), 50);
    },
  },
  // ---------------------------------------------------------------- STAZIONE (19 + 22)
  {
    id: "stazione",
    n: 26, livello: 5, autonomo: true,
    icona: "📟",
    nome: "Stazione LCD: meteo + distanza",
    descr: "Termometro e metro insieme: un pulsante cambia la pagina del display, tre LED mostrano sempre la distanza.",
    collegamenti: [
      "Display LCD come nel progetto 15, ma con il potenziometro del contrasto nelle colonne 29-31-33",
      "DHT11: S → pin 2, + → riga +, – → riga –",
      "HC-SR04: Vcc → riga +, Gnd → riga –, Trig → pin 3, Echo → pin 4",
      "Pulsante «pagina» con due cavetti maschio-femmina: un piedino → pin 5, quello opposto in diagonale → riga –",
      "LED verde → A0, giallo → A1, rosso → A2 (corto → 220 Ω → riga –)",
    ],
    monta(el, api) {
      const lcd = h("div", { class: "lcdbox" }, h("div", {}, "Stazione UNO Lab"), h("div", {}, "avvio...        "));
      const pag = [h("button", { onclick: () => api.invia("P0") }, "🌡️ Meteo"), h("button", { onclick: () => api.invia("P1") }, "📏 Distanza")];
      const t = h("div", { class: "grande" }, "–"), u = h("div", { class: "grande" }, "–");
      const mm = h("p", { class: "etichetta centro" }, "");
      const dist = h("div", { class: "distanza" }, "–");
      const colori = ["#16a065", "#e0a800", "#d43c3c"];
      const leds = colori.map(c => h("div", { class: "lampada piccola", "data-c": c }));
      let dati = { t: null, d: null, pagina: 0 };
      function aggiornaLcd() {
        const r = dati.pagina === 0
          ? (dati.t && +dati.t[0] > -50 ? [`${dati.t[0].padStart(3)}°C  Umid ${dati.t[1].padStart(2)}%`, `min ${dati.t[2].padStart(2)}  max ${dati.t[3].padStart(2)}`] : ["Meteo: sensore", "non risponde"])
          : (dati.d === null ? ["Distanza: --", ""] : dati.d < 0 ? ["Distanza: --", ""]
            : [`Dist ${dati.d.toFixed(1).padStart(5)} cm`, "█".repeat(Math.max(0, Math.min(16, Math.round(dati.d / 200 * 16))))]);
        lcd.children[0].textContent = r[0].padEnd(16); lcd.children[1].textContent = r[1].padEnd(16);
      }
      el.append(lcd,
        h("div", { class: "schede due" }, ...pag),
        h("p", { class: "etichetta centro" }, "Il pulsante sulla breadboard fa la stessa cosa"),
        h("div", { class: "griglia2" },
          h("div", { class: "misura" }, h("p", { class: "etichetta" }, "Temperatura"), t),
          h("div", { class: "misura" }, h("p", { class: "etichetta" }, "Umidità"), u)),
        mm,
        h("p", { class: "etichetta" }, "Distanza e LED"),
        h("div", { class: "riga centro" }, ...leds), dist,
        h("button", { onclick: () => api.invia("Z") }, "Azzera minima e massima"));
      api.onRiga(l => {
        let m;
        if ((m = l.match(/^T (-?\d+) (-?\d+) (-?\d+) (-?\d+)/))) {
          dati.t = [m[1], m[2], m[3], m[4]];
          const ok = +m[1] > -50;
          t.textContent = ok ? m[1] + " °C" : "–"; u.textContent = ok ? m[2] + " %" : "–";
          mm.textContent = ok ? `minima ${m[3]} °C · massima ${m[4]} °C` : "Il DHT11 non risponde: controlla i 3 fili.";
        } else if ((m = l.match(/^D (-?[\d.]+) (\d)/))) {
          dati.d = parseFloat(m[1]);
          dist.textContent = dati.d < 0 ? "niente davanti (oltre 3 m)" : dati.d.toFixed(1) + " cm";
          leds.forEach((x, i) => { const on = i === +m[2]; x.style.background = on ? x.dataset.c : ""; x.style.boxShadow = on ? `0 0 14px ${x.dataset.c}` : "none"; });
        } else if ((m = l.match(/^P (\d)/))) {
          dati.pagina = +m[1];
          pag.forEach((b, i) => b.classList.toggle("attiva", i === dati.pagina));
        } else return;
        aggiornaLcd();
      });
    },
  },
];

PROGETTI.sort((a, b) => a.n - b.n);
export const LIVELLI = ["", "Livello 1 · Primi passi", "Livello 2 · Sensori", "Livello 3 · Moduli e chip", "Livello 4 · Motori", "Livello 5 · Progetti autonomi (anche a batteria)"];
