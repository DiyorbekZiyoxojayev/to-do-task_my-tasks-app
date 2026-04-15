// Bo'sh service worker - faqat o'rnatish uchun, keshlamaslik
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.map(k => caches.delete(k))))
    .then(() => self.clients.claim())
  );
});
self.addEventListener('fetch', e => {
  // Hech narsa keshlamaymiz - har doim tarmoqdan olamiz
  e.respondWith(fetch(e.request));
});
