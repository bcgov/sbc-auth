import Axios from 'axios'
import ConfigHelper from '@/util/config-helper'

var mockob = {
  'VUE_APP_COPS_REDIRECT_URL': 'https://coops-dev.pathfinder.gov.bc.ca/',
  'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1',
  'VUE_APP_AUTH_ROOT_API': 'https://auth-api-dev.pathfinder.gov.bc.ca/api/v1'
}

jest.mock('axios', () => ({
  get: jest.fn(() => Promise.resolve({ data: { mockob } })),
  all: jest.fn(),
  post: jest.fn(),
  put: jest.fn()
}), {
  virtual: true
})

beforeEach(() => {
  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockob)
  jest.clearAllMocks()
})

describe('ConfigHelper tests', () => {
  it('does not Call Axios config when session storage is present', () => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockob)
    ConfigHelper.saveConfigToSessionStorage()
    expect(Axios.get).toBeCalledTimes(0)
  })
})

// sessionStorage.clear()

// describe('ConfigHelper tests', () => {
//   sessionStorage.clear()
//   let url = `${process.env.VUE_APP_PATH}config/configuration.json`
//   it('Call Axios config when no session storage is present', () => {
//     sessionStorage.clear()
//     ConfigHelper.saveConfigToSessionStorage()
//     expect(Axios.get).toBeCalledTimes(1)
//     expect(Axios.get).toBeCalledWith(url)
//   })
// })
