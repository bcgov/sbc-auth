import Axios from 'axios'
import KeycloakServices from '../../src/services/keycloak.services'

jest.mock('axios', () => ({
  get: jest.fn(),
  all: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  patch: jest.fn()
}), {
  virtual: true
})
var mockKcJosn = {
  'realm': 'test',
  'auth-server-url': 'https://sso-dev.pathfinder.gov.bc.ca/auth',
  'ssl-required': 'external',
  'resource': 'sbc-auth-web',
  'verify-token-audience': true,
  'credentials': {
    'secret': 'aeb2b9bc-672b-4574-8bc8-e76e853c37cb'
  },
  'use-resource-role-mappings': true,
  'confidential-port': 0
}

describe('initialize keycloak', () => {
  const results = []
  beforeAll(() => {
    // @ts-ignore
    Axios.get.mockClear()
    // @ts-ignore
    Axios.all.mockResolvedValue(results)
  })

  it('should clear session storage ', () => {
    expect(sessionStorage.getItem('KEYCLOAK_TOKEN')).toEqual(null)
    expect(sessionStorage.getItem('KEYCLOAK_REFRESH_TOKEN')).toEqual(null)
  })
})
