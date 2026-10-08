// 쉬어갈카 서비스워커 — 버전을 올리면 옛 캐시를 지운다.
// 변경점: ① 버전 v4로 올려 옛 저장본 정리  ② 화면(HTML)을 받을 때 브라우저 임시 저장본을 건너뛰고 서버에 확인  ③ 받은 최신 화면을 오프라인용 저장본에도 갱신
const CACHE = 'shigeo-v4';
const SHELL = ['./', './index.html', './manifest.json', './rest_areas_master.json'];
const CDN = ['unpkg.com', 'cdnjs.cloudflare.com', 'cdn.jsdelivr.net'];

self.addEventListener('install', (e) => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).catch(() => {}));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // 화면: 네트워크 먼저(서버에 새 파일이 있는지 매번 확인), 끊기면 저장본
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req, { cache: 'no-cache' })
        .then((res) => {
          if (res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put('./index.html', copy)); }
          return res;
        })
        .catch(() => caches.match('./index.html'))
    );
    return;
  }
  // 휴게소 데이터: 저장본을 먼저 보여 주고 뒤에서 갱신
  if (url.origin === location.origin && url.pathname.endsWith('.json')) {
    e.respondWith(caches.open(CACHE).then(async (c) => {
      const hit = await c.match(req, { ignoreSearch: true });
      const net = fetch(req).then((res) => { if (res.ok) c.put(req, res.clone()); return res; }).catch(() => hit);
      return hit || net;
    }));
    return;
  }
  // 라이브러리·글꼴(CDN): 버전 고정 주소라 저장본 우선
  if (CDN.includes(url.hostname)) {
    e.respondWith(caches.open(CACHE).then(async (c) => {
      const hit = await c.match(req);
      if (hit) return hit;
      const res = await fetch(req);
      if (res.ok || res.type === 'opaque') c.put(req, res.clone());
      return res;
    }));
  }
  // 카카오·오피넷·지도 타일 등 나머지는 브라우저에 맡긴다
});
