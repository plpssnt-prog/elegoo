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
];
