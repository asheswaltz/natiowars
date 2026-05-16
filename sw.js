const CACHE_NAME = 'nation-wars-v1';
const CORE_ASSETS = [
  './',
  './index.html',
  './i18n.js',
  './levels.js',
  './maintheme.mp3',
  './manifest.webmanifest',
  './img/app-icon.svg',
  './img/world.png',
  './img/westeurope3countries.png',
  './img/south america.png',
  './img/north america.png',
  './img/europe.png',
  './img/asia.png',
  './img/afrique.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(CORE_ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;

      return fetch(event.request)
        .then(response => {
          if (!response || response.status !== 200 || response.type === 'opaque') {
            return response;
          }

          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseClone));
          return response;
        })
        .catch(() => caches.match('./index.html'));
    })
  );
});