// TaskVault Pro - Service Worker
// Muhim: App o'rnatilganda to'g'ri ishlashi uchun network-first strategiya

const CACHE = "taskvault-pro-v2";

self.addEventListener("install", e => {
  // Darhol faollashadi
  self.skipWaiting();
});

self.addEventListener("activate", e => {
  // Barcha eski keshlarni o'chirib tashlaydi
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", e => {
  // HTML fayllar uchun: DOIM tarmoqdan ol, keyin keshla
  if (e.request.mode === "navigate" || e.request.url.endsWith(".html")) {
    e.respondWith(
      fetch(e.request)
        .then(res => {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
          return res;
        })
        .catch(() => caches.match(e.request))
    );
    return;
  }

  // Boshqa fayllar: keshdan ol, yo'q bo'lsa tarmoqdan
  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) return cached;
      return fetch(e.request).then(res => {
        if (!res || res.status !== 200 || res.type === "opaque") return res;
        const clone = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, clone));
        return res;
      });
    })
  );
});
