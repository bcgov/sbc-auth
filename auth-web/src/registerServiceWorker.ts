/* eslint-disable no-console */

import { register } from 'register-service-worker'

if (process.env.NODE_ENV === 'production') {
  register(`${process.env.BASE_URL}service-worker.js`, {
    ready () {
      console.log(
        'App is being served from cache by a service worker.\n' +
        'For more details, visit https://goo.gl/AFskqB'
      )
    },
    registered (event) {
      console.log('Service worker has been registered.')
    },
    cached () {
      console.log('Content has been cached for offline use.')
    },
    updatefound () {
      console.log('New content is downloading.')
    },
    updated (updatedEvent) {
      // write code for popup here
      console.log('New content is available; refreshing page in 1 sec')
      // showInteractiveToastReload('New content is available!', updatedEvent)

      updatedEvent.waiting.postMessage({ action: 'skipWaiting' })
      // timeout is for the service worker to get activated
      setTimeout(() => {
        window.location.reload(true)
      }, 1000)
    },
    offline () {
      // add offline indication here
      console.log('No internet connection found. App is running in offline mode.')
    },
    error (error) {
      console.error('Error during service worker registration:', error)
    }
  })
}
