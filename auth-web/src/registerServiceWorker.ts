import { register } from 'register-service-worker'

if (process.env.NODE_ENV === 'production') {
  register(`${process.env.BASE_URL}service-worker.js`, {
    updated () {
      // remove older cached content
      // ref: https://santhoshkumarravi.medium.com/vue-pwa-disable-5463e44b1f7f
      caches.keys().then(names => {
        for (let name of names) caches.delete(name)
      })
    }
  })
}
