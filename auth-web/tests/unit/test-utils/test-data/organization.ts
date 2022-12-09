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
