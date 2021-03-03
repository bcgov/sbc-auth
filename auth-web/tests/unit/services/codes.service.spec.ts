import { Code } from '@/models/Code'
import CodesService from '../../../src/services/codes.service'
import axios from 'axios'

var mockob = {
  'VUE_APP_COPS_REDIRECT_URL': 'https://coops-dev.pathfinder.gov.bc.ca/',
  'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1',
  'VUE_APP_AUTH_ROOT_API': 'https://auth-api-dev.pathfinder.gov.bc.ca/api/v1'
}

describe('Codes service', () => {
  beforeAll(() => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockob)
    // @ts-ignore
    jest.clearAllMocks()
  })

  it('call getCodes() for suspended_reason_codes ', () => {
    jest.mock('axios')
    const testCodeSuspensionReasons: Code[] = [{
      code: 'testSuspensionCode',
      desc: 'testSuspensionDesc',
      default: true
    }]
    const resp = { data: testCodeSuspensionReasons }
    axios.get = jest.fn().mockReturnValue(resp)

    CodesService.getCodes('suspension-reason-codes').then((response) => {
      expect(response).toEqual(testCodeSuspensionReasons)
    })
  })
})
