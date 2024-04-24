// service-worker.js

// set names for both precache & runtime cache
workbox.core.setCacheNameDetails({
  prefix: 'dev-jonghoonpark',
  suffix: 'v1.3',
  precache: 'precache',
  runtime: 'runtime-cache'
});

// let Service Worker take control of pages ASAP
workbox.skipWaiting();
workbox.clientsClaim();

// let Workbox handle our precache list
workbox.precaching.precacheAndRoute(self.__precacheManifest);

// use `NetworkFirst` strategy for root page
workbox.routing.registerRoute(
  /^\/$/,
  new workbox.strategies.NetworkFirst()
);

// use `NetworkFirst` strategy for html
workbox.routing.registerRoute(
  /\.html$/,
  new workbox.strategies.NetworkFirst()
);

// use `NetworkFirst` strategy for css and js
workbox.routing.registerRoute(
  /\.(?:js|css)$/,
  new workbox.strategies.NetworkFirst()
);

// use `CacheFirst` strategy for images
workbox.routing.registerRoute(
  /assets\/(images|icons)/,
  new workbox.strategies.CacheFirst()
);