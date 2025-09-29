// Service Worker para SIBIA PWA
const CACHE_NAME = 'sibia-v1.0.0';
const urlsToCache = [
  '/',
  '/static/js/main.js',
  '/static/index.html',
  '/static/biodigestor_background.jpg',
  '/static/manifest.json',
  // Agregar más recursos según sea necesario
];

// Instalación del Service Worker
self.addEventListener('install', event => {
  console.log('SIBIA SW: Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('SIBIA SW: Caching files');
        return cache.addAll(urlsToCache);
      })
      .catch(error => {
        console.log('SIBIA SW: Cache failed', error);
      })
  );
});

// Activación del Service Worker
self.addEventListener('activate', event => {
  console.log('SIBIA SW: Activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('SIBIA SW: Deleting old cache', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Interceptar solicitudes de red
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Si está en cache, devolver desde cache
        if (response) {
          return response;
        }

        // Si no está en cache, intentar obtener de la red
        return fetch(event.request)
          .then(response => {
            // Verificar si la respuesta es válida
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Clonar la respuesta
            const responseToCache = response.clone();

            // Agregar al cache solo recursos estáticos
            if (event.request.url.includes('/static/') || 
                event.request.url.endsWith('/')) {
              caches.open(CACHE_NAME)
                .then(cache => {
                  cache.put(event.request, responseToCache);
                });
            }

            return response;
          })
          .catch(() => {
            // Si falla la red, mostrar página offline si es HTML
            if (event.request.destination === 'document') {
              return caches.match('/offline.html');
            }
          });
      })
  );
});

// Manejo de mensajes desde la aplicación
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// Notificación push (opcional para futuras funcionalidades)
self.addEventListener('push', event => {
  if (event.data) {
    const options = {
      body: event.data.text(),
      icon: '/static/icon-192x192.png',
      badge: '/static/icon-72x72.png',
      vibrate: [100, 50, 100],
      data: {
        dateOfArrival: Date.now(),
        primaryKey: 1
      },
      actions: [
        {
          action: 'explore',
          title: 'Ver SIBIA',
          icon: '/static/icon-96x96.png'
        },
        {
          action: 'close',
          title: 'Cerrar',
          icon: '/static/icon-96x96.png'
        }
      ]
    };

    event.waitUntil(
      self.registration.showNotification('SIBIA Notification', options)
    );
  }
});

// Manejo de clics en notificaciones
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

console.log('SIBIA Service Worker loaded successfully'); 