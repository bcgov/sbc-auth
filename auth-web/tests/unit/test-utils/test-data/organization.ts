import { AccessType, AccountStatus } from '@/util/constants'
import { OrgAccountTypes, Organization } from '@/models/Organization'

// default basic values
const organization: Organization = {
  'accessType': AccessType.REGULAR,
  'id': 1,
  'name': 'test org',
  'orgType': OrgAccountTypes.BASIC,
  'statusCode': AccountStatus.ACTIVE
}

export const getTestOrg = (params?: any): Organization => {
  const newOrg = { ...organization }
  if (params) {
    const keys = Object.keys(params)
    for (const i in keys) newOrg[keys[i]] = params[keys[i]]
  }
  return newOrg
}

export const orgsDetailsByAffiliationEmptyResponse = {
  'orgsDetails': []
}
export const orgsDetailsByAffiliationSingleItemResponse = {
  'orgsDetails': [
    {
      'name': 'NEW BC ONLINE TECH TEAM',
      'uuid': '47f1fb02-87d0-4a28-954e-4aed84231036'
    }
  ]
}

export const orgsDetailsByAffiliationMultipleItemsResponse = {
  'orgsDetails': [
    {
      'name': 'Updated new testing account',
      'uuid': '19833670-08e6-4309-abc3-20e7b116fd60'
    },
    {
      'name': 'mytest updated',
      'uuid': '6c3588df-dfe2-46d4-a644-07ef4a32ddd1'
    },
    {
      'name': 'Manchester United',
      'uuid': 'edf5e343-a82e-4079-9daf-56ae73b5343a'
    }
  ]
}
