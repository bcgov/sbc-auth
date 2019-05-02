import Axios from 'axios'
const AUTHENTICATION_RESOURCE_NAME = '/authenticate'

export default {
  emit (framewindow :Window, token:string) {
    console.log('process.env.VUE_APP_COPS_REDIRECT_URL in Iframe' + process.env.VUE_APP_COPS_REDIRECT_URL + 'token' + token)
    framewindow.postMessage(token, process.env.VUE_APP_COPS_REDIRECT_URL)
  }
}
