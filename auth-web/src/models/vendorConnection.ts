export interface VendorConnection {
  id: string
  serviceProviderName: string
  dateAdded: string
  createdBy: string
  expiryDate: string
  status?: string
}

/** GET /orgs/{orgId}/linking-keys response item — see auth-api AccountLinkingKeySchema. */
export interface AccountLinkingKey {
  id: number
  accountId: number
  vendorAccountId?: number
  vendorAccountName?: string
  expiresOn: string
  createdOn: string
  createdBy?: string
  lastUsed?: string
  status?: string
}

export interface AccountLinkingKeysResponse {
  linkingKeys: AccountLinkingKey[]
}

export interface LinkingKeyActionDetails {
  orgId: number
  keyId: number
}

/**
 * Linking key status values — API (see LinkingKeyStatus enum) plus UI-derived expiry states.
 * Badge labels in UX are all uppercase (EXPIRED, EXPIRES IN X DAYS, PENDING).
 */
export const VendorConnectionStatuses = {
  Active: 'ACTIVE',
  Pending: 'PENDING',
  Revoked: 'REVOKED',
  Expiring: 'EXPIRING',
  Expired: 'EXPIRED'
} as const

export type VendorConnectionStatus = typeof VendorConnectionStatuses[keyof typeof VendorConnectionStatuses]
