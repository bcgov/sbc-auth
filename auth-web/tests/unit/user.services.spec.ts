import Axios from 'axios'
import UserService from '../../src/services/user.services'

jest.mock('axios', () => ({
  get: jest.fn(),
  all: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  patch: jest.fn()
}), {
  virtual: true
})
var mockob = {
  'VUE_APP_COPS_REDIRECT_URL': 'https://coops-dev.pathfinder.gov.bc.ca/',
  'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1',
  'VUE_APP_AUTH_ROOT_API': 'https://auth-api-dev.pathfinder.gov.bc.ca/api/v1'
}

describe('Get user profile', () => {
  const results = []
  beforeAll(() => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockob)
    // @ts-ignore
    Axios.get.mockClear()
    // @ts-ignore
    Axios.all.mockResolvedValue(results)
    // @ts-ignore
    UserService.getUserProfile('@me')
  })

  it('should call Axios.get ', () => {
    expect(Axios.get).toHaveBeenCalledWith(`${mockob.VUE_APP_AUTH_ROOT_API}/users/@me`)
    expect(Axios.get).toBeCalledTimes(1)
  })
})
