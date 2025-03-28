import * as Sentry from '@sentry/browser'
import Axios from 'axios'
import ConfigHelper from '@/util/config-helper'
import { SessionStorageKeys } from '@/util/constants'

const axios = Axios.create()

axios.interceptors.request.use(
  request => {
    // Bypass adding auth header for googcle cloud store
    if (request.url?.includes('storage.googleapis.com')) {
      return request
    }

    request.headers['App-Name'] = import.meta.env.APP_NAME
    const token = ConfigHelper.getFromSession(SessionStorageKeys.KeyCloakToken)
    if (token) {
      request.headers.Authorization = `Bearer ${token}`
    }
    return request
  },
  error => Promise.reject(error)
)

axios.interceptors.response.use(
  response => response,
  error => {
    Sentry.captureException(error)
    return Promise.reject(error)
  }
)

export { axios }
