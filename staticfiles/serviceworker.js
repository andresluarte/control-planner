// static/serviceworker.js
const CACHE_NAME = 'construapp-v1';
const urlsToCache = [
    '/',
    '/static/construccion1app/css/estilos.css',
    '/static/construccion1app/img/logo2.jpeg'
];

// Instalación del Service Worker
self.addEventListener('install', function(event) {
    console.log('Service Worker instalado');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('Cache abierto');
                return cache.addAll(urlsToCache);
            })
    );
});

// Activación del Service Worker
self.addEventListener('activate', function(event) {
    console.log('Service Worker activado');
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Eliminando cache antiguo:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Interceptar peticiones
self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                return response || fetch(event.request);
            })
    );
});

// Manejar notificaciones push
self.addEventListener('push', function(event) {
    console.log('Push recibido:', event);
    const data = event.data ? event.data.json() : {};
    const title = data.title || "Nueva notificación";
    const options = {
        body: data.body || "Tienes una nueva notificación",
        icon: '/static/construccion1app/img/logo2.jpeg',
        badge: '/static/construccion1app/img/logo2.jpeg',
        vibrate: [200, 100, 200],
        data: {
            url: data.url || '/'
        }
    };
    
    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

// Manejar clicks en notificaciones
self.addEventListener('notificationclick', function(event) {
    console.log('Click en notificación');
    event.notification.close();
    
    const urlToOpen = event.notification.data.url || '/';
    
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then(function(clientList) {
                // Si ya hay una ventana abierta, enfócala
                for (let i = 0; i < clientList.length; i++) {
                    const client = clientList[i];
                    if (client.url === urlToOpen && 'focus' in client) {
                        return client.focus();
                    }
                }
                // Si no, abre una nueva ventana
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
    );
});