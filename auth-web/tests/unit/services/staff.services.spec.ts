import { ProductsRequestBody } from '@/models/Staff'
import StaffService from '../../../src/services/staff.services'

vi.mock('../../../src/services/staff.services')
const mockob = {
  'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1',
  'AUTH_API_URL': 'https://auth-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
}

const mockProducts : ProductsRequestBody = {
  subscriptions: [
    {
      productCode: 'ppr',
      productRoles: ['search']
    }
  ]
}

const spyGetProducts = vi.spyOn(StaffService, 'getProducts')
const spyGetAccountTypes = vi.spyOn(StaffService, 'getAccountTypes')
const spyAddProducts = vi.spyOn(StaffService, 'addProducts')

describe('Get staff service', () => {
  beforeEach(() => {
    sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(mockob)
    vi.clearAllMocks()

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
