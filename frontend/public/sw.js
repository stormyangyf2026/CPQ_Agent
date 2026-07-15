// CPQ Agent App — Service Worker
const CACHE_NAME = 'cpq-agent-v1';

const PRECACHE_URLS = [
  '/',
  '/index.html',
];

// Install: 预缓存核心资源
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
  );
  self.skipWaiting();
});

// Activate: 清理旧缓存
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch: NetworkFirst (API) / CacheFirst (静态资源) / StaleWhileRevalidate (第三方)
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  const isApi = url.pathname.startsWith('/agent/') || url.pathname.startsWith('/config');
  const isStatic = /\.(js|css|png|svg|ico|woff2?)$/.test(url.pathname);

  if (isApi) {
    // API: NetworkFirst
    event.respondWith(
      fetch(event.request)
        .then((resp) => {
          const cloned = resp.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, cloned));
          return resp;
        })
        .catch(() => caches.match(event.request))
    );
  } else if (isStatic) {
    // Static: CacheFirst
    event.respondWith(
      caches.match(event.request).then((cached) => cached || fetch(event.request))
    );
  } else {
    // Other: StaleWhileRevalidate
    event.respondWith(
      caches.match(event.request).then((cached) => {
        const fetchPromise = fetch(event.request).then((resp) => {
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, resp.clone()));
          return resp;
        });
        return cached || fetchPromise;
      })
    );
  }
});
