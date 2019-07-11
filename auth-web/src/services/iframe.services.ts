import Axios from 'axios'
import ConfigHelper from '../util/config-helper'
const AUTHENTICATION_RESOURCE_NAME = '/authenticate'

export default {
  emit (framewindow :Window, msg:string) {
    console.log('Emit VUE_APP_COPS_REDIRECT_URL' + ConfigHelper.getValue('VUE_APP_COPS_REDIRECT_URL'))
    framewindow.postMessage(msg, ConfigHelper.getValue('VUE_APP_COPS_REDIRECT_URL'))
  }
}
