
import { AccountLinkingKey, VendorConnection, VendorConnectionStatuses } from '@/models/vendorConnection'
import { LDFlags, Role } from '@/util/constants'
import { MembershipType } from '@/models/Organization'
import { getLdFlag } from '@/util/flag-util'
import moment from 'moment'

export const VENDOR_CONNECTION_EXPIRY_WARNING_DAYS = 30

export function isAccountLinkingDisabled (): boolean {
  return getLdFlag(LDFlags.DisableAccountLinking, true)
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
 * Extend linking keys — Admin/Coordinator (account_holder JWT),
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

export function canRevokeVendorConnection (
  membershipTypeCode: MembershipType | undefined,
  userRoles: string[] = []
): boolean {
  if (!canViewVendorConnections(membershipTypeCode, userRoles)) {
    return false
  }

  return membershipTypeCode === MembershipType.Admin
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
export function getVendorConnectionStatus (expiryDate: string, keyStatus?: string): string | undefined {
  const today = moment().startOf('day')
  const expiry = moment(expiryDate).startOf('day')

  if (expiry.isBefore(today)) {
    return VendorConnectionStatuses.Expired
  }

  const normalizedStatus = keyStatus?.toUpperCase()
  const isNearExpiry = expiry.diff(today, 'days') <= VENDOR_CONNECTION_EXPIRY_WARNING_DAYS

  if (normalizedStatus === VendorConnectionStatuses.Active && isNearExpiry) {
    return VendorConnectionStatuses.Expiring
  }

  return normalizedStatus
}

export function showsStandaloneRemoveAction (connectionStatus?: string): boolean {
  return connectionStatus === VendorConnectionStatuses.Active ||
    connectionStatus === VendorConnectionStatuses.Pending
}

export function getDaysUntilExpiry (expiryDate: string): number {
  const today = moment().startOf('day')
  const expiry = moment(expiryDate).startOf('day')
  return Math.max(0, expiry.diff(today, 'days'))
}

export function isValidVendorLinkingParams (vendorAccountId: string, returnUrl: string): boolean {
  if (!vendorAccountId || !/^\d+$/.test(vendorAccountId)) {
    return false
  }
  if (!returnUrl) {
    return false
  }
  try {
    return ['http:', 'https:'].includes(new URL(returnUrl).protocol)
  } catch {
    return false
  }
}

/**
 * Builds the /signin/:idpHint/:redirectUrl(.*) path for a given destination URL.
 *
 * That route decodes its :redirectUrl(.*) param twice before use — once by vue-router's own
 * param matching, then again by SigninView.vue's explicit decodeURIComponent — so a
 * destinationUrl that itself carries a query string (as ours does, e.g. vendorAccountId +
 * returnUrl) must be encoded twice going in, or its own `&`-separated params get misread as
 * extra route path segments and silently truncated after the first `&`. See
 * VendorLinkingLoginCard.spec.ts for a test that decodes the result exactly as production does.
 */
export function buildSigninPath (idpHint: string, destinationUrl: string): string {
  return `/signin/${idpHint}/${encodeURIComponent(encodeURIComponent(destinationUrl))}`
}
