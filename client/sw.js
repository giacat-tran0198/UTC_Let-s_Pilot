/* eslint-disable no-restricted-globals */
/* eslint-disable no-undef */

// ---------- Cache handler ---------- //

importScripts(
  'https://storage.googleapis.com/workbox-cdn/releases/6.1.5/workbox-sw.js'
);

//Set to true for log
workbox.setConfig({ debug: false });

//Point of injection for injectManifest command
workbox.precaching.precacheAndRoute(self.__WB_MANIFEST);

// Cache the Google Fonts stylesheets with a stale-while-revalidate strategy.
workbox.routing.registerRoute(
  ({ url }) => url.origin === 'https://fonts.googleapis.com',
  new workbox.strategies.StaleWhileRevalidate({
    cacheName: 'google-fonts-stylesheets',
  })
);

// Cache the underlying font files with a cache-first strategy for 1 year.
workbox.routing.registerRoute(
  ({ url }) => url.origin === 'https://fonts.gstatic.com',
  new workbox.strategies.CacheFirst({
    cacheName: 'google-fonts-webfonts',
    plugins: [
      new workbox.cacheableResponse.CacheableResponse({
        statuses: [0, 200],
      }),
      new workbox.expiration.CacheExpiration({
        maxAgeSeconds: 60 * 60 * 24 * 365,
        maxEntries: 30,
      }),
    ],
  })
);

workbox.routing.registerRoute(
  ({request}) => request.destination === 'image',
  new workbox.strategies.CacheFirst({
    cacheName: 'images',
    plugins: [
       new workbox.expiration.CacheExpiration({
        maxEntries: 60,
        maxAgeSeconds: 30 * 24 * 60 * 60, // 30 Days
      }),
    ],
  })
);

// ---------- Push Notification handler ---------- //

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

  // Open the link in browser when user click on notification
  //event.waitUntil(clients.openWindow('https://www.tx_chat.com'));
});

