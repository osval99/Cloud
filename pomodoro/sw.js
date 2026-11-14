const CACHE_NAME = "pomodoro-v1";
const APP_SHELL = ["./", "./index.html", "./manifest.json", "./icon.svg"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((c) => c.addAll(APP_SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    fetch(event.request, { cache: "no-store" })
      .then((r) => {
        if (r.ok) { const copy = r.clone(); caches.open(CACHE_NAME).then((c) => c.put(event.request, copy)); }
        return r;
      })
      .catch(() => caches.match(event.request))
  );
});

// Al tocar la notificación, enfocar la app
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(
    self.clients.matchAll({ type: "window" }).then((list) =>
      list.length ? list[0].focus() : self.clients.openWindow("./index.html")
    )
  );
});
