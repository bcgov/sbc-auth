import Axios from 'axios'
import UserService from '../../src/services/user.services'
import { Contact } from '../../src/models/contact'

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

var mockContact : Contact = {
  email: 'test@test.com',
  phone: '555-555-5555',
  phoneExtension: '123'
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
    UserService.createUserProfile()
    UserService.createContact(mockContact)
  })

  it('should call get users ', () => {
    expect(Axios.get).toHaveBeenCalledWith(`${mockob.VUE_APP_AUTH_ROOT_API}/users/@me`)
    expect(Axios.get).toBeCalledTimes(1)
  })

  it('should call create users and contacts ', () => {
    expect(Axios.post).toHaveBeenCalledWith(`${mockob.VUE_APP_AUTH_ROOT_API}/users`, {})
    expect(Axios.post).toHaveBeenCalledWith(`${mockob.VUE_APP_AUTH_ROOT_API}/users/contacts`, mockContact)
  })
})
