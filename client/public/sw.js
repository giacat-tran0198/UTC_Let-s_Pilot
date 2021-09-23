/* eslint-disable no-undef */
/* eslint-disable no-restricted-globals */
self.addEventListener('push', (event) => {
  //console.log('[Service Worker] : ', JSON.parse(event.data.text()));
  const data = JSON.parse(event.data.text());
  event.waitUntil(
    self.registration.showNotification('Tx Chat', {
      body: data.data.message,
      icon: '../image/logo192.png',
      vibrate: [200, 100, 200],
      renotify: true,
      tag: 'txChatMessage',
      badge: '../image/logo72.png',
      lang: 'EN',
    })
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  event.waitUntil(clients.openWindow('https://google.com'));
});
