import Axios from 'axios'
const AUTHENTICATION_RESOURCE_NAME = '/authenticate'

export default {
  emit (framewindow :Window, msg:string) {
    console.log('process.env.VUE_APP_COPS_REDIRECT_URL in Iframe' + process.env.VUE_APP_COPS_REDIRECT_URL + 'msg' + msg)
    framewindow.postMessage(msg, process.env.VUE_APP_COPS_REDIRECT_URL)
  }
}
