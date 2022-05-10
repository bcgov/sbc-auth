import Axios from 'axios'
import { ProductsRequestBody } from '@/models/Staff'
import StaffService from '../../../src/services/staff.services'

jest.mock('../../../src/services/staff.services')
/*
jest.mock('axios', () => ({
  create: jest.fn(() => Promise.resolve({ data: { }})),
  get: jest.fn(() => Promise.resolve({ data: {mockob}})),
  all: jest.fn(),
  post: jest.fn(() => Promise.resolve({ data: {}})),
  put: jest.fn(),
  patch: jest.fn()
}), {
  virtual: true
})
*/
var mockob = {
  'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1',
  'AUTH_API_URL': 'https://auth-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
}

var mockProducts : ProductsRequestBody = {
  subscriptions: [
    {
      productCode: 'ppr',
      productRoles: ['search']
    }
  ]
}

const spyGetProducts = jest.spyOn(StaffService, 'getProducts')
const spyGetAccountTypes = jest.spyOn(StaffService, 'getAccountTypes')
const spyAddProducts = jest.spyOn(StaffService, 'addProducts')

describe('Get staff service', () => {
  const results = []
  beforeEach(() => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockob)
    jest.clearAllMocks()

    StaffService.getProducts()
    StaffService.getAccountTypes()
    StaffService.addProducts(1, mockProducts)
  })

  it('should call get products ', () => {
    expect(spyGetProducts).toHaveBeenCalledTimes(1)
  })

  it('should call get account types ', () => {
    expect(spyGetAccountTypes).toHaveBeenCalledTimes(1)
  })

  it('should call add products ', () => {
    expect(spyAddProducts).toHaveBeenCalledWith(1, mockProducts)
  })
})
