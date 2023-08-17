import PaymentServices from '../../../src/services/payment.services'

vi.mock('../../../src/services/payment.services')

const mockob = {
  'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1',
  'AUTH_API_URL': 'https://auth-api-dev.apps.silver.devops.gov.bc.ca/api/v1',
  'VUE_APP_FLAVOR': 'post-mvp'
}

describe('create a transaction', () => {
  beforeAll(() => {
    sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(mockob)
    vi.clearAllMocks()
  })

  it('should call create transaction ', () => {
    const spyCreateTransaction = vi.spyOn(PaymentServices, 'createTransaction')
    PaymentServices.createTransaction('paymentId', 'www.redirecturl.com')
    expect(spyCreateTransaction).toBeCalledTimes(1)
    expect(spyCreateTransaction).toHaveBeenCalledWith('paymentId', 'www.redirecturl.com')
  })

  it('should call update transaction without receipt number ', () => {
    const spyUpdateTransaction = vi.spyOn(PaymentServices, 'updateTransaction')
    PaymentServices.updateTransaction('paymentId', 'transactionId')
    expect(spyUpdateTransaction).toBeCalledTimes(1)
    expect(spyUpdateTransaction).toHaveBeenCalledWith('paymentId', 'transactionId')
  })
})
