/* eslint-disable no-console */

import ConfigHelper from './util/config-helper'
import { SessionStorageKeys } from './util/constants'
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
      // remove older cached content
      // ref: https://santhoshkumarravi.medium.com/vue-pwa-disable-5463e44b1f7f
      caches.keys().then(names => {
        for (const name of names) {
          caches.delete(name)
        }
      })

      // Remove Launch Darkly files from session if new build content is downloaded
      // Once the app is reloaded after the timeout, the App.vue will initialize the LD againx
      // Otherwise, user will only get the LD flags if he/she signout-and-signin or restart-browser
      ConfigHelper.removeFromSession(SessionStorageKeys.LaunchDarklyFlags)

      navigator.serviceWorker.controller.postMessage({ action: 'skipWaiting' })
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
