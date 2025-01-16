import { useOrgStore } from "@/stores"
import ConfigHelper from "@/util/config-helper"
import { AccessType, PaymentTypes, SessionStorageKeys } from "@/util/constants"

export const useAccountCreate = () => {
  async function save (state, createAccount) {
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
        state.errorMessage = bcolAccountDetails ? null : 'Error - No account details provided for this account.'
        orgStore.setCurrentOrganizationBcolProfile(state.currentOrganization.bcolProfile)
      } catch (err) {
        switch (err.response.status) {
          case 409:
            break
          case 400:
            state.errorMessage = err.response.data.message?.detail || err.response.data.message
            break
          default:
            state.errorMessage = 'An error occurred while attempting to create your account.'
        }
      }
      if (!state.errorMessage) {
        createAccount()
      }
    }

    return {
      save
    }
}
