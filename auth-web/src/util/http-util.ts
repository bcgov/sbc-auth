import * as Sentry from '@sentry/browser'
import Axios from 'axios'
import ConfigHelper from '@/util/config-helper'
import { SessionStorageKeys } from '@/util/constants'

const axios = Axios.create()

axios.interceptors.request.use(
  request => {
    // Bypass adding auth header for minio
    if (request.url?.includes('minio')) {
      return request
    }

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
