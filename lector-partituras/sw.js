// App: primero la red (para tomar cambios). Librerías del CDN: primero la caché (tienen versión fija).
const CACHE = "atril-v1";
const SHELL = ["./", "./index.html", "./manifest.json", "./icon.svg"];
const LIBS = [
  "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js",
  "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js",
  "https://cdn.jsdelivr.net/npm/opensheetmusicdisplay@1.8.9/build/opensheetmusicdisplay.min.js",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then(async (c) => {
    await c.addAll(SHELL);
    await Promise.all(LIBS.map((u) => c.add(new Request(u, { mode: "cors" })).catch(() => {})));
  }));
  self.skipWaiting();
});
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener("fetch", (e) => {
  const url = e.request.url;
  if (e.request.method !== "GET") return;
  if (LIBS.includes(url) || url.startsWith("https://fonts.")) {
    e.respondWith(caches.match(e.request).then((hit) => hit || fetch(e.request).then((r) => {
      if (r.ok) { const cp = r.clone(); caches.open(CACHE).then((c) => c.put(e.request, cp)); }
      return r;
    })));
    return;
  }
  if (new URL(url).origin !== location.origin) return;
  e.respondWith(fetch(e.request, { cache: "no-store" }).then((r) => {
    if (r.ok) { const cp = r.clone(); caches.open(CACHE).then((c) => c.put(e.request, cp)); }
    return r;
  }).catch(() => caches.match(e.request)));
});
