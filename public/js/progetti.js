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
    nome: "Servo",
    descr: "Muove il servo SG90 da 0° a 180° con uno slider.",
    collegamenti: [
      "Marrone → GND",
      "Rosso → 5V",
      "Arancione → pin 9",
    ],
    monta(el, api) {
      const lancetta = h("div", { class: "lancetta" });
      const valore = h("div", { class: "grande" }, "90°");
      const invia = limitato(v => api.invia("A" + v));
      const imposta = v => {
        valore.textContent = v + "°";
        lancetta.style.transform = `rotate(${v - 90}deg)`;
        s.value = v;
        invia(v);
      };
      const s = slider(0, 180, 90, imposta);
      el.append(
        h("div", { class: "quadrante" }, lancetta, h("div", { class: "perno" })),
        valore, s,
        h("div", { class: "griglia5" },
          ...[0, 45, 90, 135, 180].map(a => h("button", { onclick: () => imposta(a) }, a + "°"))));
      lancetta.style.transform = "rotate(0deg)";
      setTimeout(() => api.invia("A90"), 50);
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
