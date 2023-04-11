import axios from 'axios'
import TokenService from 'sbc-common-components/src/services/token.services'

export default function setup () {
  axios.interceptors.request.use(function (config) {
    const token = sessionStorage.getItem('KEYCLOAK_TOKEN')
    const tracingID = sessionStorage.getItem('REGISTRIES_TRACE_ID')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    if (tracingID) {
      config.headers['registries-trace-id'] = tracingID
    }
    return config
  }, function (err) {
    return Promise.reject(err)
  })
  // enable to do an interceptor which will refresh the token on 401 failures
  // createAxiosResponseInterceptor()
}

function createAxiosResponseInterceptor () {
  const interceptor = axios.interceptors.response.use(
    (response) => { return response },
    error => {
      // eslint-disable-next-line no-console
      console.log('error url:' + error.config.url)
      const originalRequest = error.config
      if (error.response.status !== 401) {
        return new Promise((resolve, reject) => {
          reject(error)
        })
      }
      axios.interceptors.response.eject(interceptor)
      if (error.response.status === 401) {
        originalRequest._retry = true
        const tokenservice = new TokenService()
        tokenservice.init().then(function (token) {
          originalRequest.headers['Authorization'] = `Bearer ${token}`
          return axios(originalRequest)
        }).catch(error => {
          // cant refresh..Probably refresh token expired
          return Promise.reject(error)
        }).finally(createAxiosResponseInterceptor)
      }
    })
}
