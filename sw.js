const CACHE = "taskvault-pro-v3";
const BASE = "/to-do-task_my-tasks-app";

self.addEventListener("install", e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll([
      BASE + "/",
      BASE + "/index.html",
      BASE + "/manifest.json",
      BASE + "/icon-192.png",
      BASE + "/icon-512.png"
    ])).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", e => {
  if (e.request.mode === "navigate") {
    e.respondWith(
      fetch(e.request)
        .then(res => {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
          return res;
        })
        .catch(() => caches.match(BASE + "/index.html"))
    );
    return;
  }
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request).then(res => {
      if (!res || res.status !== 200 || res.type === "opaque") return res;
      caches.open(CACHE).then(c => c.put(e.request, res.clone()));
      return res;
    }))
  );
});
