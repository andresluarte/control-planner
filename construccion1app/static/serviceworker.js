self.addEventListener('push', function(event) {
    const data = event.data.json();
    const title = data.head || "Notificación";
    const options = {
        body: data.body || "",
        icon: "/static/construccion1app/img/logo2.jpeg",
        data: data.url || "/"
    };
    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    const url = event.notification.data;
    event.waitUntil(
        clients.openWindow(url)
    );
});
