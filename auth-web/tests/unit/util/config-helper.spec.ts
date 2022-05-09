import Axios from 'axios'
import ConfigHelper from '@/util/config-helper'

var mockob = {
  'PAY_API_URL': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1',
  'AUTH_API_URL': 'https://auth-api-dev.apps.silver.devops.gov.bc.ca/api/v1',
  'NRO_URL': 'https://dev.bcregistrynames.gov.bc.ca/nro/',
  'NAME_REQUEST_URL': 'https://dev.bcregistry.ca/namerequest/'
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

// TOFIX fix later
describe('ConfigHelper tests', () => {
  xit('does make one Call Axios config when session storage is present', () => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockob)
    ConfigHelper.saveConfigToSessionStorage()
    expect(Axios.get).toBeCalled()
    // expect(true).toEqual(true)
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
