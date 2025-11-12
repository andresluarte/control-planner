self.addEventListener('push', function(event) {
    const data = event.data ? event.data.json() : {};
    const title = data.title || "Nueva notificación";
    const options = {
        body: data.body || "Tienes una nueva notificación",
        icon: '/static/img/icon.png', // opcional
        badge: '/static/img/badge.png' // opcional
    };
    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow('/')
    );
});
