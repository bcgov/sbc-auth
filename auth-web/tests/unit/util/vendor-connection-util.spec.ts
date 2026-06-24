import { LDFlags, Role } from '@/util/constants'
import { canAccessVendorConnections, mapLinkingKeyToVendorConnection } from '@/util/vendor-connection-util'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import { MembershipType } from '@/models/Organization'

describe('vendor-connection-util', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('canAccessVendorConnections', () => {
    it('returns false when disable-account-linking flag is on', () => {
      vi.spyOn(LaunchDarklyService, 'getFlag').mockReturnValue(true)

      expect(canAccessVendorConnections(MembershipType.Admin, [Role.AccountHolder])).toBe(false)
      expect(LaunchDarklyService.getFlag).toHaveBeenCalledWith(LDFlags.DisableAccountLinking, false)
    })

    it('returns false without account_holder or manage_accounts JWT role', () => {
      vi.spyOn(LaunchDarklyService, 'getFlag').mockReturnValue(false)

      expect(canAccessVendorConnections(MembershipType.Admin, [])).toBe(false)
      expect(canAccessVendorConnections(MembershipType.Admin, [Role.Staff])).toBe(false)
    })

    it('returns true for Admin with account_holder role', () => {
      vi.spyOn(LaunchDarklyService, 'getFlag').mockReturnValue(false)

      expect(canAccessVendorConnections(
        MembershipType.Admin,
        [Role.AccountHolder]
      )).toBe(true)
    })

    it('returns true for Coordinator with account_holder role', () => {
      vi.spyOn(LaunchDarklyService, 'getFlag').mockReturnValue(false)

      expect(canAccessVendorConnections(
        MembershipType.Coordinator,
        [Role.AccountHolder]
      )).toBe(true)
    })

    it('returns false for regular User even with account_holder role', () => {
      vi.spyOn(LaunchDarklyService, 'getFlag').mockReturnValue(false)

      expect(canAccessVendorConnections(
        MembershipType.User,
        [Role.AccountHolder]
      )).toBe(false)
    })

    it('returns true for staff with manage_accounts role', () => {
      vi.spyOn(LaunchDarklyService, 'getFlag').mockReturnValue(false)

      expect(canAccessVendorConnections(
        undefined,
        [Role.Staff, Role.StaffManageAccounts]
      )).toBe(true)
    })

    it('returns true for external staff with manage_accounts role', () => {
      vi.spyOn(LaunchDarklyService, 'getFlag').mockReturnValue(false)

      expect(canAccessVendorConnections(
        undefined,
        [Role.ExternalStaffReadonly, Role.StaffManageAccounts]
      )).toBe(true)
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
        expiresOn: '2027-01-15T00:00:00Z'
      })).toEqual({
        id: '42',
        serviceProviderName: 'ABC API Service',
        dateAdded: '2026-01-15T11:20:00Z',
        createdBy: 'William Smith',
        expiryDate: '2027-01-15T00:00:00Z'
      })
    })
  })
})
