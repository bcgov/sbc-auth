import axios from 'axios'

export default function setup () {
  axios.interceptors.request.use(function (config) {
    const token = sessionStorage.getItem('KEYCLOAK_TOKEN')
    const tracingID = sessionStorage.getItem('REGISTRIES_TRACE_ID')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    debugger
    if (tracingID) {
      config.headers['registries-tracing-id'] = tracingID
    }
    return config
  }, function (err) {
    return Promise.reject(err)
  })
}
