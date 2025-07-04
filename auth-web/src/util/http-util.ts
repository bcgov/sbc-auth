import Axios from 'axios'
import ConfigHelper from '@/util/config-helper'
import { SessionStorageKeys } from '@/util/constants'

const axios = Axios.create()

axios.interceptors.request.use(
  request => {
    // Bypass adding auth header for googcle cloud store
    const url = new URL(request.url)
    const allowedHosts = ['storage.googleapis.com']
    if (allowedHosts.includes(url.host)) {
      return request
    }

    request.headers['App-Name'] = import.meta.env.APP_NAME
    const token = ConfigHelper.getFromSession(SessionStorageKeys.KeyCloakToken)
    if (token) {
      request.headers.Authorization = `Bearer ${token}`
    }
    const authApiUrl = ConfigHelper.getAuthAPIUrl()
    const authApiKey = import.meta.env.VUE_APP_AUTH_API_KEY
    if (authApiKey && request.url.includes(authApiUrl)) {
      request.headers['x-apikey'] = authApiKey
    }
    return request
  },
  error => Promise.reject(error)
)

axios.interceptors.response.use(
  response => response,
  error => {
    return Promise.reject(error)
  }
)

export { axios }
