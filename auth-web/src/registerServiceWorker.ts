/* eslint-disable no-console */

import Swal from 'sweetalert2'
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
      console.log('SW 2 URL: ', event.active.scriptURL)
      console.log('SW 2 state: ', event.active.state)
    },
    cached (event) {
      console.log('Content has been cached for offline use.')
      console.log(event)
    },
    updatefound (event) {
      console.log('New content is downloading.')
      console.log(event)
    },
    updated (updatedEvent) {
      // write code for popup here
      console.log('New content is available; please refresh.')
      showInteractiveToastReload('New content is available!', updatedEvent)
      console.log(updatedEvent)
      console.log(updatedEvent.waiting)
    },
    offline () {
      // add offline indication here
      console.log('No internet connection found. App is running in offline mode.')
    },
    error (error) {
      console.error('Error during service worker registration:', error)
    }
  })

  const showInteractiveToastReload = (text, updatedEvent) => {
    const Toast = Swal.mixin({
      toast: true,
      position: 'bottom-right',
      showConfirmButton: true,
      confirmButtonText: 'Refresh',
      timer: 0,
      width: '100',
      grow: 'fullscreen',
      padding: '1.3rem 3rem'
    })

    Toast.fire({
      icon: 'info',
      title: text
    }).then((result) => {
      if (result.value) {
        updatedEvent.waiting.postMessage({ action: 'skipWaiting' })
      }
    })
  }
}
