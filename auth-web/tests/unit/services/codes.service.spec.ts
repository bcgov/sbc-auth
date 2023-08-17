import { Code } from '@/models/Code'
import CodesService from '../../../src/services/codes.service'

const mockob = {
  'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1',
  'AUTH_API_URL': 'https://auth-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
}

describe('Codes service', () => {
  beforeAll(() => {
    sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(mockob)
    vi.clearAllMocks()
  })

  it('call getCodes() for suspended_reason_codes ', () => {
    const testCodeSuspensionReasons: Code[] = [{
      code: 'testSuspensionCode',
      desc: 'testSuspensionDesc',
      default: true
    }]
    vi.doMock('axios', () => {
      return {
        get: vi.fn().mockReturnValue({ data: testCodeSuspensionReasons }),
        interceptors: {
          request: {
            use: vi.fn(),
            eject: vi.fn()
          },
          response: {
            use: vi.fn(),
            eject: vi.fn()
          }
        }
      }
    })
    CodesService.getCodes('suspension-reason-codes').then((response) => {
      expect(response).toEqual(testCodeSuspensionReasons)
    })
  })
})
