
import { AccountLinkingKey, VendorConnection, VendorConnectionStatus } from '@/models/vendorConnection'
import { LDFlags, Role } from '@/util/constants'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import { MembershipType } from '@/models/Organization'
import moment from 'moment'

export const VENDOR_CONNECTION_EXPIRY_WARNING_DAYS = 30

/**
 * Matches auth-api org_linking_keys access:
 * - JWT: account_holder or manage_accounts
 * - Org: Admin/Coordinator, unless staff/external staff bypass
 * - Feature flag disable-account-linking hides the page
 */
export function canAccessVendorConnections (
  membershipTypeCode: MembershipType | undefined,
  userRoles: string[] = []
): boolean {
  if (LaunchDarklyService.getFlag(LDFlags.DisableAccountLinking, false)) {
    return false
  }

  const hasJwtRole = userRoles.includes(Role.AccountHolder) ||
    userRoles.includes(Role.StaffManageAccounts)
  const canBypassOrgRole = userRoles.includes(Role.Staff) ||
    userRoles.includes(Role.ExternalStaffReadonly)
  const isOrgOwner = [MembershipType.Admin, MembershipType.Coordinator].includes(membershipTypeCode)

  return hasJwtRole && (canBypassOrgRole || isOrgOwner)
}

export function mapLinkingKeyToVendorConnection (linkingKey: AccountLinkingKey): VendorConnection {
  return {
    id: String(linkingKey.id),
    serviceProviderName: linkingKey.vendorAccountName || '',
    dateAdded: linkingKey.createdOn,
    createdBy: linkingKey.createdBy || '',
    expiryDate: linkingKey.expiresOn
  }
}

export function getVendorConnectionStatus (expiryDate: string): VendorConnectionStatus {
  const today = moment().startOf('day')
  const expiry = moment(expiryDate).startOf('day')

  if (expiry.isBefore(today)) {
    return 'expired'
  }
  if (expiry.diff(today, 'days') <= VENDOR_CONNECTION_EXPIRY_WARNING_DAYS) {
    return 'expiring'
  }
  return 'active'
}

export function getDaysUntilExpiry (expiryDate: string): number {
  const today = moment().startOf('day')
  const expiry = moment(expiryDate).startOf('day')
  return Math.max(0, expiry.diff(today, 'days'))
}
