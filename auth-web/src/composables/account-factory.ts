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
  const isPremiumAccount = () => currentOrganization.value?.orgType === Account.PREMIUM

  const isRegularAccount = () => currentOrganization.value?.accessType === AccessType.REGULAR

  const anonAccount = () => currentOrganization.value?.accessType === AccessType.ANONYMOUS

  const isGovmAccount = () => currentOrganization.value?.accessType === AccessType.GOVM

  const isGovnAccount = () => currentOrganization.value?.accessType === AccessType.GOVN

  const isStaffAccount = () => currentOrganization.value?.orgType === Account.STAFF

  const isSbcStaffAccount = () => currentOrganization.value?.orgType === Account.SBC_STAFF

  return {
    anonAccount,
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
