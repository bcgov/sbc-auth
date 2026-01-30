import { AccessType, PaymentTypes, SessionStorageKeys } from '@/util/constants'
import { getErrorMessage, isErrorType, normalizeError } from '@/util/error-util'
import ConfigHelper from '@/util/config-helper'
import { useOrgStore } from '@/stores'

export const useAccountCreate = () => {
  async function save (state, createAccount, errorDialog) {
    const orgStore = useOrgStore()
    orgStore.setCurrentOrganizationPaymentType(state.selectedPaymentMethod)
    // Update Access Type, in case user select GOVN
    const isGovNAccount = !!JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.GOVN_USER || 'false'))
    if (isGovNAccount) {
      orgStore.setAccessType(AccessType.GOVN)
      orgStore.setCurrentOrganization({ ...orgStore.currentOrganization, accessType: AccessType.GOVN })
    }
    if (state.selectedPaymentMethod !== PaymentTypes.BCOL) {
      // It's possible this is already set from being linked, so we need to empty it out.
      orgStore.setCurrentOrganizationBcolProfile(null)
      createAccount()
      return
    }
    try {
      const bcolAccountDetails = await orgStore.validateBcolAccount(state.currentOrganization.bcolProfile)
      state.errorText = bcolAccountDetails ? null : 'Error - No account details provided for this account.'
      orgStore.setCurrentOrganizationBcolProfile(state.currentOrganization.bcolProfile)
    } catch (err) {
      const normalized = normalizeError(err)
      switch (normalized.status) {
        case 409:
          // Conflict - do nothing
          break
        case 400:
          state.errorText = getErrorMessage(normalized)
          break
        default:
          state.errorText = 'An error occurred while attempting to create your account.'
      }
      errorDialog.value.open()
    }
    if (!state.errorText) {
      createAccount()
    }
  }

  function handleCreateAccountError (state, err) {
    const normalized = normalizeError(err)
    switch (normalized.status) {
      case 409:
        state.errorText = 'An account with this name already exists. Try a different account name.'
        break
      case 400:
        if (isErrorType(normalized, 'MAX_NUMBER_OF_ORGS_LIMIT')) {
          state.errorText = 'Maximum number of accounts reached'
        } else if (isErrorType(normalized, 'ACTIVE_AFFIDAVIT_EXISTS')) {
          state.errorText = getErrorMessage(normalized) || 'Affidavit already exists'
        } else {
          state.errorText = 'An error occurred while attempting to create your account.'
        }
        break
      default:
        state.errorText = 'An error occurred while attempting to create your account.'
    }
  }

  return {
    save,
    handleCreateAccountError
  }
}
