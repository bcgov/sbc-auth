import { AccessType, PaymentTypes, SessionStorageKeys } from '@/util/constants'
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
      orgStore.setCurrentOrganization({ ...state.currentOrganization, accessType: AccessType.GOVN })
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
      switch (err.response.status) {
        case 409:
          break
        case 400:
          state.errorText = err.response.data.message?.detail || err.response.data.message
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
    switch (err?.response?.status) {
      case 409:
        state.errorText =
                'An account with this name already exists. Try a different account name.'
        break
      case 400:
        switch (err.response.data?.code) {
          case 'MAX_NUMBER_OF_ORGS_LIMIT':
            state.errorText = 'Maximum number of accounts reached'
            break
          case 'ACTIVE_AFFIDAVIT_EXISTS':
            state.errorText = err.response.data.message || 'Affidavit already exists'
            break
          default:
            state.errorText = 'An error occurred while attempting to create your account.'
        }
        break
      default:
        state.errorText =
                'An error occurred while attempting to create your account.'
    }
  }

  return {
    save,
    handleCreateAccountError
  }
}
