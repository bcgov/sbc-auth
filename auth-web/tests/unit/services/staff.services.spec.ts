import Axios from 'axios'
import { ProductsRequestBody } from '@/models/Staff'
import StaffService from '../../../src/services/staff.services'

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

var mockProducts : ProductsRequestBody = {
  subscriptions: [
    {
      productCode: 'ppr',
      productRoles: ['search']
    }
  ]
}

describe('Get staff service', () => {
  const results = []
  beforeEach(() => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockob)
    // @ts-ignore
    Axios.get.mockClear()
    // @ts-ignore
    Axios.all.mockResolvedValue(results)

    StaffService.getProducts()
    StaffService.getAccountTypes()
    StaffService.addProducts(1, mockProducts)
  })

  it('should call get products ', () => {
    expect(Axios.get).toHaveBeenCalledWith(`${mockob.VUE_APP_AUTH_ROOT_API}/codes/product_code`)
  })

  it('should call get org types ', () => {
    expect(Axios.get).toHaveBeenCalledWith(`${mockob.VUE_APP_AUTH_ROOT_API}/codes/org_type`)
  })

  it('should call add products ', () => {
    expect(Axios.post).toHaveBeenCalledWith(`${mockob.VUE_APP_AUTH_ROOT_API}/orgs/1/products`, mockProducts)
  })
})
