
import { AccountLinkingKey, VendorConnection, VendorConnectionStatuses } from '@/models/vendorConnection'
import { LDFlags, Role } from '@/util/constants'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import { MembershipType } from '@/models/Organization'
import moment from 'moment'

export const VENDOR_CONNECTION_EXPIRY_WARNING_DAYS = 30

function isAccountLinkingDisabled (): boolean {
  return LaunchDarklyService.getFlag(LDFlags.DisableAccountLinking, true)
}

function hasLinkingKeysJwtRole (userRoles: string[] = []): boolean {
  return userRoles.includes(Role.AccountHolder) ||
    userRoles.includes(Role.StaffManageAccounts)
}

function isStaffUser (userRoles: string[] = []): boolean {
  return userRoles.includes(Role.Staff) ||
    userRoles.includes(Role.ExternalStaffReadonly)
}

function isOrgMember (membershipTypeCode: MembershipType | undefined): boolean {
  return [
    MembershipType.Admin,
    MembershipType.Coordinator,
    MembershipType.User
  ].includes(membershipTypeCode)
}

function isStaffWithManageAccounts (userRoles: string[] = []): boolean {
  if (!userRoles.includes(Role.StaffManageAccounts)) {
    return false
  }
  return userRoles.includes(Role.Staff) ||
    userRoles.includes(Role.ExternalStaffReadonly)
}

/**
 * View linking-keys list — all team members (and staff).
 * Matches auth-api org_linking_keys GET access.
 */
export function canViewVendorConnections (
  membershipTypeCode: MembershipType | undefined,
  userRoles: string[] = []
): boolean {
  if (isAccountLinkingDisabled()) {
    return false
  }

  if (!hasLinkingKeysJwtRole(userRoles)) {
    return false
  }

  return isStaffUser(userRoles) || isOrgMember(membershipTypeCode)
}

/**
 * Remove/extend linking keys — Admin/Coordinator (account_holder JWT),
 * or staff/external staff with manage_accounts (matches org_linking_keys PR #3819).
 */
export function canManageVendorConnections (
  membershipTypeCode: MembershipType | undefined,
  userRoles: string[] = []
): boolean {
  if (!canViewVendorConnections(membershipTypeCode, userRoles)) {
    return false
  }

  if (isStaffWithManageAccounts(userRoles)) {
    return true
  }

  return [MembershipType.Admin, MembershipType.Coordinator].includes(membershipTypeCode)
}

export function mapLinkingKeyToVendorConnection (linkingKey: AccountLinkingKey): VendorConnection {
  return {
    id: String(linkingKey.id),
    serviceProviderName: linkingKey.vendorAccountName || '',
    dateAdded: linkingKey.createdOn,
    createdBy: linkingKey.createdBy || '',
    expiryDate: linkingKey.expiresOn,
    status: linkingKey.status
  }
}

/**
 * Expiry date overrides API status when expired.
 * EXPIRING is UI-derived for ACTIVE keys within the warning window; other statuses pass through.
 */
export function getVendorConnectionStatus (expiryDate: string, keyStatus?: string): string {
  const today = moment().startOf('day')
  const expiry = moment(expiryDate).startOf('day')

  if (expiry.isBefore(today)) {
    return VendorConnectionStatuses.Expired
  }

  const normalizedStatus = keyStatus?.toUpperCase()
  const isNearExpiry = expiry.diff(today, 'days') <= VENDOR_CONNECTION_EXPIRY_WARNING_DAYS

  if ((!normalizedStatus || normalizedStatus === VendorConnectionStatuses.Active) && isNearExpiry) {
    return VendorConnectionStatuses.Expiring
  }

  if (normalizedStatus) {
    return normalizedStatus
  }

  return VendorConnectionStatuses.Active
}

export function showsStandaloneRemoveAction (connectionStatus: string): boolean {
  return connectionStatus === VendorConnectionStatuses.Active ||
    connectionStatus === VendorConnectionStatuses.Pending
}

export function getDaysUntilExpiry (expiryDate: string): number {
  const today = moment().startOf('day')
  const expiry = moment(expiryDate).startOf('day')
  return Math.max(0, expiry.diff(today, 'days'))
}
