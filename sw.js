// Cut Crew service worker: keeps the app opening when offline.
var CACHE='cutcrew-v5';
var FILES=['./','manifest.webmanifest','icon-192.png','icon-512.png'];
self.addEventListener('install',function(e){e.waitUntil(caches.open(CACHE).then(function(c){return c.addAll(FILES);}).catch(function(){}));self.skipWaiting();});
self.addEventListener('activate',function(e){e.waitUntil(caches.keys().then(function(ks){return Promise.all(ks.filter(function(k){return k!==CACHE;}).map(function(k){return caches.delete(k);}));}));self.clients.claim();});
// Network first, cache as backup, so new versions show up straight away.
self.addEventListener('fetch',function(e){
  if(e.request.method!=='GET'||new URL(e.request.url).origin!==self.location.origin)return;
  e.respondWith(fetch(e.request).then(function(r){var copy=r.clone();caches.open(CACHE).then(function(c){c.put(e.request,copy);});return r;}).catch(function(){return caches.match(e.request);}));
});
