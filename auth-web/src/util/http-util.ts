import * as Sentry from '@sentry/browser'
import Axios from 'axios'
import ConfigHelper from '@/util/config-helper'
import { SessionStorageKeys } from '@/util/constants'

const axios = Axios.create()

axios.interceptors.request.use(
  config => {
    // Bypass adding auth header for minio, which may otherwise break requests
    if (config.url?.includes('minio')) {
      return config
    }

    const token = ConfigHelper.getFromSession(SessionStorageKeys.KeyCloakToken)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
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
