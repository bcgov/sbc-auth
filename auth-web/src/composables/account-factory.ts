import { AccessType, Account, SessionStorageKeys } from '@/util/constants'
import { AccountSettings } from '@/models/account-settings'
import ConfigHelper from '@/util/config-helper'
import { Organization } from '@/models/Organization'
import { computed } from '@vue/composition-api'
import { useOrgStore } from '@/store/org'

export const useAccount = () => {
  const orgStore = useOrgStore()
  const currentOrganization = computed(() => orgStore.currentOrganization as Organization)

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
    getAccountFromSession,
    isPremiumAccount,
    isRegularAccount,
    anonAccount,
    isGovmAccount,
    isGovnAccount,
    isStaffAccount,
    isSbcStaffAccount
  }
}
