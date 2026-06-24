import { LDFlags, Role } from '@/util/constants'
import { AccountLinkingKey, VendorConnection, VendorConnectionStatus } from '@/models/vendorConnection'
import { MembershipType } from '@/models/Organization'
import moment from 'moment'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'

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

/** TODO(#33662): Remove Mock data for UI stub until AUTH API is available. */
export function getMockVendorConnections (): VendorConnection[] {
  const today = moment()

  return [
    {
      id: '1',
      serviceProviderName: 'ABC API Service',
      dateAdded: today.clone().subtract(2, 'months').hour(11).minute(20).toISOString(),
      createdBy: 'William Smith',
      expiryDate: today.clone().add(1, 'year').format('YYYY-MM-DD')
    },
    {
      id: '2',
      serviceProviderName: 'Beta Legal Vendor',
      dateAdded: today.clone().subtract(6, 'months').hour(9).minute(15).toISOString(),
      createdBy: 'William Smith',
      expiryDate: today.clone().add(20, 'days').format('YYYY-MM-DD')
    },
    {
      id: '3',
      serviceProviderName: 'Legacy Vendor App',
      dateAdded: today.clone().subtract(2, 'years').hour(14).minute(30).toISOString(),
      createdBy: 'William Smith',
      expiryDate: today.clone().subtract(1, 'month').format('YYYY-MM-DD')
    }
  ]
}
