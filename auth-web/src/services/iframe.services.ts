import Axios from 'axios'
import ConfigHelper from '../util/config-helper'
const AUTHENTICATION_RESOURCE_NAME = '/authenticate'

export default {
  emit (framewindow :Window, msg:string) {
    framewindow.postMessage(msg, ConfigHelper.getCoopsURL())
  }
}
