import Axios from 'axios'
import PaymentServices from '../../src/services/payment.services'

jest.mock('axios', () => ({
  get: jest.fn(),
  all: jest.fn(),
  post: jest.fn(),
  put: jest.fn()
}), {
  virtual: true
})
describe('create a transaction', () => {
  const results = []
  beforeAll(() => {
    // @ts-ignore
    Axios.get.mockClear()
    // @ts-ignore
    Axios.all.mockResolvedValue(results)
    // @ts-ignore
    PaymentServices.createTransaction('paymentId', 'www.redirecturl.com')
  })

  it('should call Axios.post ', () => {
    expect(Axios.post).toHaveBeenCalledWith(`${process.env.VUE_APP_PAY_ROOT_API}/payments/paymentId/transactions?redirect_uri=www.redirecturl.com`, {}, { 'headers': { 'Authorization': 'Bearer null' } })
    expect(Axios.post).toBeCalledTimes(1)
  })
})

describe('update a transaction', () => {
  const results = []
  beforeAll(() => {
    // @ts-ignore
    Axios.get.mockClear()
    // @ts-ignore
    Axios.all.mockResolvedValue(results)
  })

  it('should call Axios.put wihtout receipt number ', () => {
    PaymentServices.updateTransaction('paymentId', 'transactionId')
    expect(Axios.put).toHaveBeenCalledWith(`${process.env.VUE_APP_PAY_ROOT_API}/payments/paymentId/transactions/transactionId`, { 'params': '' }, { 'headers': { 'Authorization': 'Bearer null' } })
  })

  it('should call Axios.put  with receipt number', () => {
    PaymentServices.updateTransaction('paymentId', 'transactionId', 'receiptno')
    var param = { 'receipt_number': 'receiptno' }
    expect(Axios.put).toHaveBeenCalledWith(`${process.env.VUE_APP_PAY_ROOT_API}/payments/paymentId/transactions/transactionId`, { 'params': { 'receipt_number': 'receiptno' } }, { 'headers': { 'Authorization': 'Bearer null' } })
  })
})

