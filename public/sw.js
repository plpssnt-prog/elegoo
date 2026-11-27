// Service worker di UNO Lab.
// Strategia "prima la rete": se c'è connessione si scarica sempre la versione più recente
// (pagina, programmi, guide PDF); la copia salvata si usa solo senza rete.
const CACHE = "uno-lab-v2";
const BASE = ["./", "index.html", "manifest.webmanifest", "js/app.js", "js/link.js", "js/flasher.js", "js/progetti.js",
  "js/versione.js", "js/nativo.js", "icone/icona-192.png", "icone/icona-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(BASE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(k => Promise.all(k.filter(n => n !== CACHE).map(n => caches.delete(n))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;
  e.respondWith((async () => {
    try {
      const r = await fetch(req, { cache: "no-store" });
      if (r.ok) {
        const c = await caches.open(CACHE);
        c.put(req.url.split("?")[0], r.clone());   // una sola copia per file, senza ?v=
      }
      return r;
    } catch {
      const c = await caches.open(CACHE);
      return (await c.match(req.url.split("?")[0])) || (await c.match("index.html")) || Response.error();
    }
  })());
});
