import { Address } from '@/models/address'

const address: Address = {
  'city': 'Langley',
  'country': 'CA',
  'postalCode': 'V3A 7E9',
  'region': 'BC',
  'street': '446-19705 Fraser Hwy',
  'streetAdditional': ''
}

export const getTestAddress = (params?: any): Address => {
  const newAddress = { ...address }
  if (params) {
    const keys = Object.keys(params)
    for (const i in keys) newAddress[keys[i]] = params[keys[i]]
  }
  return newAddress
}
