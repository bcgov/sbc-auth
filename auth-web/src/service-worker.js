
workbox.core.setCacheNameDetails({ prefix: 'auth-web' })

self.__precacheManifest = [].concat(self.__precacheManifest || [])
workbox.precaching.suppressWarnings && workbox.precaching.suppressWarnings()
workbox.precaching.precacheAndRoute(self.__precacheManifest, {})

self.skipWaiting()
