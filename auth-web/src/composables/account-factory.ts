import { AccessType, Account, SessionStorageKeys } from '@/util/constants'
import { GLInfo, Organization } from '@/models/Organization'
import { AccountSettings } from '@/models/account-settings'
import ConfigHelper from '@/util/config-helper'
import { computed } from '@vue/composition-api'
import { useOrgStore } from '@/stores/org'

export const useAccount = () => {
  const orgStore = useOrgStore()
  const currentOrganization = computed(() => orgStore.currentOrganization as Organization)
  const currentMembership = computed(() => orgStore.currentMembership)
  const currentOrgPaymentType = computed(() => orgStore.currentOrgPaymentType)
  const currentOrgAddress = computed(() => orgStore.currentOrgAddress)
  const permissions = computed(() => orgStore.permissions)
  const currentOrgGLInfo = computed(() => orgStore.currentOrgGLInfo as GLInfo)

  const getAccountFromSession = (): AccountSettings => {
    return JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccount || '{}'))
  }

  const isPremiumAccount = computed(() => currentOrganization.value?.orgType === Account.PREMIUM)
  const isRegularAccount = computed(() => currentOrganization.value?.accessType === AccessType.REGULAR)
  const isGovmAccount = computed(() => currentOrganization.value?.accessType === AccessType.GOVM)
  const isGovnAccount = computed(() => currentOrganization.value?.accessType === AccessType.GOVN)
  const isStaffAccount = computed(() => currentOrganization.value?.orgType === Account.STAFF)
  const isSbcStaffAccount = computed(() => currentOrganization.value?.orgType === Account.SBC_STAFF)

  return {
    currentMembership,
    currentOrgAddress,
    currentOrganization,
    currentOrgGLInfo,
    currentOrgPaymentType,
    getAccountFromSession,
    isGovmAccount,
    isGovnAccount,
    isPremiumAccount,
    isRegularAccount,
    isSbcStaffAccount,
    isStaffAccount,
    permissions
  }
}
