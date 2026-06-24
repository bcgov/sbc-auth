export interface VendorConnection {
  id: string
  serviceProviderName: string
  dateAdded: string
  createdBy: string
  expiryDate: string
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

export type VendorConnectionStatus = 'active' | 'expiring' | 'expired'
