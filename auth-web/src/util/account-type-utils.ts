import { AccessType, Account } from '@/util/constants'
import { OrgAccountTypes, OrgMap, Organization } from '@/models/Organization'
import { EnumDictionary } from '@/models/util'

export const ACCOUNT_TYPE_MAP: EnumDictionary<OrgAccountTypes, OrgMap> = {
  [OrgAccountTypes.ALL]: {},
  [OrgAccountTypes.PREMIUM]: {
    accessType: [AccessType.REGULAR, AccessType.REGULAR_BCEID],
    orgType: Account.PREMIUM
  },
  [OrgAccountTypes.PREMIUM_OUT_OF_PROVINCE]: {
    accessType: [AccessType.EXTRA_PROVINCIAL],
    orgType: Account.PREMIUM
  },
  [OrgAccountTypes.GOVM]: {
    accessType: [AccessType.GOVM]
  },
  [OrgAccountTypes.GOVN]: {
    accessType: [AccessType.GOVN]
  },
  // Remove this when API is ready
  [OrgAccountTypes.DIRECTOR_SEARCH]: {
    accessType: [AccessType.ANONYMOUS]
  },
  [OrgAccountTypes.STAFF]: {
    accessType: [AccessType.GOVM],
    orgType: Account.STAFF
  },
  [OrgAccountTypes.SBC_STAFF]: {
    accessType: [AccessType.GOVM],
    orgType: Account.SBC_STAFF
  },
  [OrgAccountTypes.MAXIMUS_STAFF]: {
    accessType: [AccessType.GOVM],
    orgType: Account.MAXIMUS_STAFF
  }
}

export function getOrgAndAccessTypeFromAccountType (accountType: string): OrgMap {
  return ACCOUNT_TYPE_MAP[accountType] || {}
}

export function getAccountTypeFromOrgAndAccessType (org: Organization): string {
  const entries = Object.entries(ACCOUNT_TYPE_MAP)
  const byAccessTypeAndOrgType = entries.find(([, value]) =>
    value?.accessType?.includes(org.accessType) &&
    value?.orgType === org.orgType
  )
  if (byAccessTypeAndOrgType) {
    return byAccessTypeAndOrgType[0]
  }
  const byAccessType = entries.find(([, value]) =>
    value?.accessType?.includes(org.accessType)
  )
  if (byAccessType) {
    return byAccessType[0]
  }
  const byOrgType = entries.find(([, value]) =>
    value?.orgType === org.orgType
  )
  if (byOrgType) {
    return byOrgType[0]
  }
  return ''
}
