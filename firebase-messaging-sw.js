// firebase-messaging-sw.js (en la raíz del proyecto)
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-messaging-compat.js");

firebase.initializeApp({
  apiKey: "AIzaSyD6VyRKgYtAz6_-YudiXmOOIvX0XUfL5po",
  authDomain: "control-planner-791c6.firebaseapp.com",
  projectId: "control-planner-791c6",
  storageBucket: "control-planner-791c6.firebasestorage.app",
  messagingSenderId: "285111275489",
  appId: "1:285111275489:web:91482662cf9e86636d0ca0",
});

const messaging = firebase.messaging();

// Manejo de notificaciones en segundo plano
messaging.onBackgroundMessage(function(payload) {
  console.log("📬 Notificación en segundo plano:", payload);
  
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: "/static/construccion1app/img/logo2.jpeg",
    badge: "/static/construccion1app/img/logo2.jpeg",
    vibrate: [200, 100, 200],
    data: {
      url: payload.notification.click_action || "/"
    }
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// Manejar clic en la notificación
self.addEventListener('notificationclick', function(event) {
  console.log("🖱️ Click en notificación:", event);
  event.notification.close();
  
  // Abrir la URL especificada
  const urlToOpen = event.notification.data?.url || "/";
  
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