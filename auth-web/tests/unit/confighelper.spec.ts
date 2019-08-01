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

describe('ConfigHeloper tests', () => {
  let url = `/${process.env.VUE_APP_PATH}/config/configuration.json`
  it('does not Call Axios config when no session storage is present', () => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockob)
    ConfigHelper.saveConfigToSessionStorage()
    expect(Axios.get).toBeCalledTimes(0)
  })
})

describe('ConfigHeloper tests', () => {
  let url = `/${process.env.VUE_APP_PATH}/config/configuration.json`
  it('Call Axios config when no session storage is present', () => {
    sessionStorage.removeItem('AUTH_API_CONFIG')
    ConfigHelper.saveConfigToSessionStorage()
    expect(Axios.get).toBeCalledTimes(1)
    expect(Axios.get).toBeCalledWith(url)
  })
})
