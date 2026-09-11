const CACHE_NAME = 'rest-app-v1';

self.addEventListener('install', (e) => {
  self.skipWaiting();
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(['./index.html']))
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (e) => {
  // 화면(navigate) 요청만 서비스 워커가 관여하고,
  // 카카오/OSRM/Nominatim/휴게소 데이터 등 나머지 요청은 그대로 브라우저에 맡김
  if (e.request.mode === 'navigate') {
    e.respondWith(
      fetch(e.request).catch(() => caches.match('./index.html'))
    );
  }
});