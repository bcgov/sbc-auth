import { Code } from '@/models/Code'
import axios from 'axios'
import CodesService from '../../../src/services/codes.service'

const mockob = {
  'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1',
  'AUTH_API_URL': 'https://auth-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
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
