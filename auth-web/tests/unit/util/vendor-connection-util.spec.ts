import { LDFlags, Role, SessionStorageKeys } from '@/util/constants'
import {
  buildSigninPath,
  canManageVendorConnections,
  canRevokeVendorConnection,
  canViewVendorConnections,
  getVendorConnectionStatus,
  mapLinkingKeyToVendorConnection,
  showsStandaloneRemoveAction
} from '@/util/vendor-connection-util'
import { MembershipType } from '@/models/Organization'
import { VendorConnectionStatuses } from '@/models/vendorConnection'
import moment from 'moment'

function setDisableAccountLinkingFlag (value: boolean) {
  sessionStorage.setItem(SessionStorageKeys.LaunchDarklyFlags, JSON.stringify({
    [LDFlags.DisableAccountLinking]: value
  }))
}

describe('vendor-connection-util', () => {
  afterEach(() => {
    sessionStorage.removeItem(SessionStorageKeys.LaunchDarklyFlags)
  })

  describe('canViewVendorConnections', () => {
    it('returns false when disable-account-linking flag is on', () => {
      setDisableAccountLinkingFlag(true)

      expect(canViewVendorConnections(MembershipType.Admin, [Role.AccountHolder])).toBe(false)
    })

    it('returns false when the flag is missing (safe default)', () => {
      expect(canViewVendorConnections(MembershipType.Admin, [Role.AccountHolder])).toBe(false)
    })

    it('returns false without account_holder or manage_accounts JWT role', () => {
      setDisableAccountLinkingFlag(false)

      expect(canViewVendorConnections(MembershipType.Admin, [])).toBe(false)
      expect(canViewVendorConnections(MembershipType.Admin, [Role.Staff])).toBe(false)
    })

    it('returns true for Admin with account_holder role', () => {
      setDisableAccountLinkingFlag(false)

      expect(canViewVendorConnections(
        MembershipType.Admin,
        [Role.AccountHolder]
      )).toBe(true)
    })

    it('returns true for Coordinator with account_holder role', () => {
      setDisableAccountLinkingFlag(false)

      expect(canViewVendorConnections(
        MembershipType.Coordinator,
        [Role.AccountHolder]
      )).toBe(true)
    })

    it('returns true for regular User with account_holder role', () => {
      setDisableAccountLinkingFlag(false)

      expect(canViewVendorConnections(
        MembershipType.User,
        [Role.AccountHolder]
      )).toBe(true)
    })

    it('returns true for staff with manage_accounts role', () => {
      setDisableAccountLinkingFlag(false)

      expect(canViewVendorConnections(
        undefined,
        [Role.Staff, Role.StaffManageAccounts]
      )).toBe(true)
    })

    it('returns true for external staff with manage_accounts role', () => {
      setDisableAccountLinkingFlag(false)

      expect(canViewVendorConnections(
        undefined,
        [Role.ExternalStaffReadonly, Role.StaffManageAccounts]
      )).toBe(true)
    })
  })

  describe('canManageVendorConnections', () => {
    beforeEach(() => {
      setDisableAccountLinkingFlag(false)
    })

    it('returns true for Admin with account_holder role', () => {
      expect(canManageVendorConnections(
        MembershipType.Admin,
        [Role.AccountHolder]
      )).toBe(true)
    })

    it('returns true for Coordinator with account_holder role', () => {
      expect(canManageVendorConnections(
        MembershipType.Coordinator,
        [Role.AccountHolder]
      )).toBe(true)
    })

    it('returns false for regular User even with account_holder role', () => {
      expect(canManageVendorConnections(
        MembershipType.User,
        [Role.AccountHolder]
      )).toBe(false)
    })

    it('returns true for staff with manage_accounts role', () => {
      expect(canManageVendorConnections(
        undefined,
        [Role.Staff, Role.StaffManageAccounts]
      )).toBe(true)
    })

    it('returns true for external staff readonly with manage_accounts role', () => {
      expect(canManageVendorConnections(
        undefined,
        [Role.ExternalStaffReadonly, Role.StaffManageAccounts]
      )).toBe(true)
    })
  })

  describe('canRevokeVendorConnection', () => {
    beforeEach(() => {
      setDisableAccountLinkingFlag(false)
    })

    it('returns true for Admin with account_holder role', () => {
      expect(canRevokeVendorConnection(
        MembershipType.Admin,
        [Role.AccountHolder]
      )).toBe(true)
    })

    it('returns false for Coordinator even with account_holder role', () => {
      expect(canRevokeVendorConnection(
        MembershipType.Coordinator,
        [Role.AccountHolder]
      )).toBe(false)
    })

    it('returns false for regular User', () => {
      expect(canRevokeVendorConnection(
        MembershipType.User,
        [Role.AccountHolder]
      )).toBe(false)
    })

    it('returns false for staff with manage_accounts role', () => {
      expect(canRevokeVendorConnection(
        undefined,
        [Role.Staff, Role.StaffManageAccounts]
      )).toBe(false)
    })

    it('returns false for external staff readonly with manage_accounts role', () => {
      expect(canRevokeVendorConnection(
        undefined,
        [Role.ExternalStaffReadonly, Role.StaffManageAccounts]
      )).toBe(false)
    })

    it('returns false when the disable-account-linking flag is on', () => {
      setDisableAccountLinkingFlag(true)

      expect(canRevokeVendorConnection(
        MembershipType.Admin,
        [Role.AccountHolder]
      )).toBe(false)
    })
  })

  describe('mapLinkingKeyToVendorConnection', () => {
    it('maps auth-api linking key fields to vendor connection table row', () => {
      expect(mapLinkingKeyToVendorConnection({
        id: 42,
        accountId: 1,
        vendorAccountId: 99,
        vendorAccountName: 'ABC API Service',
        createdOn: '2026-01-15T11:20:00Z',
        createdBy: 'William Smith',
        expiresOn: '2027-01-15T00:00:00Z',
        status: 'ACTIVE'
      })).toEqual({
        id: '42',
        serviceProviderName: 'ABC API Service',
        dateAdded: '2026-01-15T11:20:00Z',
        createdBy: 'William Smith',
        expiryDate: '2027-01-15T00:00:00Z',
        status: 'ACTIVE'
      })
    })

    it('maps pending linking key without vendor name', () => {
      expect(mapLinkingKeyToVendorConnection({
        id: 43,
        accountId: 1,
        createdOn: '2026-01-15T11:20:00Z',
        createdBy: 'William Smith',
        expiresOn: '2027-01-15T00:00:00Z',
        status: VendorConnectionStatuses.Pending
      })).toEqual({
        id: '43',
        serviceProviderName: '',
        dateAdded: '2026-01-15T11:20:00Z',
        createdBy: 'William Smith',
        expiryDate: '2027-01-15T00:00:00Z',
        status: VendorConnectionStatuses.Pending
      })
    })
  })

  describe('showsStandaloneRemoveAction', () => {
    it('returns true for active and pending connections', () => {
      expect(showsStandaloneRemoveAction(VendorConnectionStatuses.Active)).toBe(true)
      expect(showsStandaloneRemoveAction(VendorConnectionStatuses.Pending)).toBe(true)
    })

    it('returns false for expiring and expired connections', () => {
      expect(showsStandaloneRemoveAction(VendorConnectionStatuses.Expiring)).toBe(false)
      expect(showsStandaloneRemoveAction(VendorConnectionStatuses.Expired)).toBe(false)
    })
  })

  describe('getVendorConnectionStatus', () => {
    const today = moment().startOf('day')

    it('returns expired when expiry date is in the past', () => {
      const expiryDate = today.clone().subtract(1, 'day').format('YYYY-MM-DD')

      expect(getVendorConnectionStatus(expiryDate, VendorConnectionStatuses.Active))
        .toBe(VendorConnectionStatuses.Expired)
    })

    it('returns key status when not expired', () => {
      const expiryDate = today.clone().add(1, 'year').format('YYYY-MM-DD')

      expect(getVendorConnectionStatus(expiryDate, 'suspended')).toBe('SUSPENDED')
    })

    it('returns pending for unbound linking keys', () => {
      const expiryDate = today.clone().add(1, 'year').format('YYYY-MM-DD')

      expect(getVendorConnectionStatus(expiryDate, VendorConnectionStatuses.Pending))
        .toBe(VendorConnectionStatuses.Pending)
    })

    it('normalizes ACTIVE and applies expiring warning window', () => {
      const expiryDate = today.clone().add(20, 'days').format('YYYY-MM-DD')

      expect(getVendorConnectionStatus(expiryDate, VendorConnectionStatuses.Active))
        .toBe(VendorConnectionStatuses.Expiring)
    })

    it('normalizes ACTIVE to active when outside warning window', () => {
      const expiryDate = today.clone().add(1, 'year').format('YYYY-MM-DD')

      expect(getVendorConnectionStatus(expiryDate, VendorConnectionStatuses.Active))
        .toBe(VendorConnectionStatuses.Active)
    })

    it('returns undefined when key status is omitted', () => {
      const expiryDate = today.clone().add(1, 'year').format('YYYY-MM-DD')

      expect(getVendorConnectionStatus(expiryDate)).toBeUndefined()
    })

    it('returns undefined when key status is omitted even within warning window', () => {
      const expiryDate = today.clone().add(20, 'days').format('YYYY-MM-DD')

      expect(getVendorConnectionStatus(expiryDate)).toBeUndefined()
    })
  })

  describe('buildSigninPath', () => {
    // The /signin/:idpHint/:redirectUrl(.*) route decodes its param twice before use: once
    // by vue-router's own param matching, once by SigninView.vue's explicit
    // decodeURIComponent. Confirms final result is what we expect.
    function decodeAsProductionDoes (encoded: string): string {
      return decodeURIComponent(decodeURIComponent(encoded))
    }

    it('prefixes the path with /signin/:idpHint/', () => {
      const path = buildSigninPath('bcsc', 'https://example.com/confirm')
      expect(path.startsWith('/signin/bcsc/')).toBe(true)
    })

    it('round-trips a destination URL with its own & -joined query params intact', () => {
      const destinationUrl = 'https://example.com/confirm?vendorAccountId=123&returnUrl=' +
        encodeURIComponent('https://vendor.example.com/callback?ref=abc&x=1')

      const path = buildSigninPath('bcsc', destinationUrl)
      const encoded = path.replace('/signin/bcsc/', '')

      expect(decodeAsProductionDoes(encoded)).toBe(destinationUrl)
    })
  })
})
