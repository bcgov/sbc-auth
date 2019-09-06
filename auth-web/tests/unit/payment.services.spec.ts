import Axios from 'axios'
import PaymentServices from '../../src/services/payment.services'

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
  'VUE_APP_AUTH_ROOT_API': 'https://auth-api-dev.pathfinder.gov.bc.ca/api/v1',
  'VUE_APP_FLAVOR': 'post-mvp'
}

describe('create a transaction', () => {
  const results = []
  beforeAll(() => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockob)
    // @ts-ignore
    Axios.get.mockClear()
    // @ts-ignore
    Axios.all.mockResolvedValue(results)
    // @ts-ignore
    PaymentServices.createTransaction('paymentId', 'www.redirecturl.com')
  })

  it('should call Axios.post ', () => {
    expect(Axios.post).toHaveBeenCalledWith(`${mockob.VUE_APP_PAY_ROOT_API}/payment-requests/paymentId/transactions?redirect_uri=www.redirecturl.com`, {})
    expect(Axios.post).toBeCalledTimes(1)
  })

  it('should call Axios.put wihtout receipt number ', () => {
    PaymentServices.updateTransaction('paymentId', 'transactionId')
    expect(Axios.patch).toHaveBeenCalledWith(`${mockob.VUE_APP_PAY_ROOT_API}/payment-requests/paymentId/transactions/transactionId?receipt_number=undefined`)
  })

  it('should call Axios.put  with receipt number', () => {
    PaymentServices.updateTransaction('paymentId', 'transactionId', 'receiptno')
    expect(Axios.patch).toHaveBeenCalledWith(`${mockob.VUE_APP_PAY_ROOT_API}/payment-requests/paymentId/transactions/transactionId?receipt_number=receiptno`)
  })
})
