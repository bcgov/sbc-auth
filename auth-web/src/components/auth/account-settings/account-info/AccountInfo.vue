<template>
  <v-container>
    <header class="view-header mb-9">
      <h2 class="view-header__title">
        Account Info
      </h2>
    </header>
    <div>
      <v-form ref="editAccountForm">
        <v-alert
          v-show="errorMessage"
          type="error"
          class="mb-6"
        >
          {{ errorMessage }}
        </v-alert>

        <v-alert
          v-show="warningMessage"
          type="warning"
          icon="$error"
          class="mb-6 custom-warning"
        >
          {{ warningMessage }}
        </v-alert>

        <div v-show="!anonAccount">
          <div class="nv-list-item mb-6">
            <div
              id="accountNumber"
              class="name font-weight-bold"
            >
              Account Number
            </div>
            <div
              class="value"
              aria-labelledby="accountNumber"
            >
              <div
                class="value__title"
                data-test="div-account-number"
              >
                {{ currentOrganization.id }}
              </div>
            </div>
          </div>
          <div
            v-if="isStaff"
            class="nv-list-item mb-10"
          >
            <div
              id="accountStatusStaff"
              class="name font-weight-bold"
            >
              Account Status
            </div>
            <div class="value-column">
              <div
                class="value"
                aria-labelledby="accountStatusStaff"
              >
                <v-chip
                  small
                  label
                  class="font-weight-bold white--text"
                  :color="getStatusColor(currentOrganization.orgStatus)"
                  data-test="chip-account-status"
                >
                  {{ getStatusText(currentOrganization.orgStatus) }}
                </v-chip>
              </div>
              <v-btn
                v-if="isSuspendButtonVisible"
                large
                aria-label="Suspend Account"
                title="Suspend Account"
                class="suspend-account-btn mx-1 mb-3"
                data-test="btn-suspend-account"
                @click="showSuspendAccountDialog(currentOrganization.orgStatus)"
              >
                {{
                  isAccountStatusActive
                    ? 'Suspend Account'
                    : 'Unsuspend Account'
                }}
              </v-btn>
            </div>
          </div>
          <div class="nv-list-item mb-0">
            <div
              id="accountType"
              class="name font-weight-bold"
            >
              Account Type
            </div>
            <div class="value-column">
              <div
                class="value"
                aria-labelledby="accountType"
              >
                <div class="value__title">
                  {{ accountType }}
                </div>
              </div>
            </div>
          </div>
          <AccountAccessType
            :organization="currentOrganization"
            :viewOnlyMode="isAccessTypeViewOnly"
            :currentOrgPaymentType="currentOrgPaymentType"
            :canChangeAccessType="canChangeAccessType"
            @update:viewOnlyMode="viewOnlyMode"
            @update:updateAndSaveAccessTypeDetails="updateAndSaveAccessTypeDetails"
          />
          <div
            v-if="currentOrganization.bcolAccountDetails"
            class="nv-list-item mb-6"
          >
            <div
              id="accountName"
              class="name mt-3 font-weight-bold"
            >
              Linked BC Online Account Details
            </div>
            <div class="value">
              <LinkedBCOLBanner
                :bcolAccountName="currentOrganization.bcolAccountName"
                :bcolAccountDetails="currentOrganization.bcolAccountDetails"
              />
            </div>
          </div>
          <v-divider class="my-6" />
        </div>

        <div
          v-if="isAdminContactViewable"
          class="nv-list-item mb-10"
        >
          <div
            id="adminContact"
            class="name"
          >
            Account Contact
          </div>
          <div
            class="value"
            aria-labelledby="adminContact"
          >
            <OrgAdminContact />
          </div>
        </div>

        <!-- show/edit account details -->
        <AccountDetails
          :accountDetails="accountDetails"
          :isBusinessAccount="isBusinessAccount"
          :nameChangeAllowed="!nameChangeNotAllowed"
          :viewOnlyMode="isAccountInfoViewOnly"
          @update:updateAndSaveAccountDetails="updateAndSaveAccountDetails"
          @update:viewOnlyMode="viewOnlyMode"
        />

        <template v-if="originalAddress">
          <div v-can:VIEW_ADDRESS.hide>
            <v-divider class="mt-3 mb-5" />
            <!-- TODO: can use v-can instead of v-if if all user with change permisson have view also -->
            <AccountMailingAddress
              ref="mailingAddress"
              :baseAddress="originalAddress"
              :viewOnlyMode="isAddressViewOnly"
              @update:address="updateAddress"
              @valid="checkBaseAddressValidity"
              @update:updateDetails="updateDetails"
              @update:resetAddress="resetAddress"
              @update:viewOnlyMode="viewOnlyMode"
            />
          </div>
        </template>
        <div>
          <v-divider class="mt-3 mb-10" />
          <div class="form__btns">
            <v-btn
              v-if="isDeactivateButtonVisible"
              v-can:DEACTIVATE_ACCOUNT.hide
              text
              color="primary"
              class="deactivate-btn font-weight-bold"
              data-test="deactivate-btn"
              to="/account-deactivate"
            >
              Deactivate Account
            </v-btn>
          </div>
        </div>
      </v-form>
    </div>
    <!-- Suspend Account Dialog -->
    <ModalDialog
      ref="suspendAccountDialog"
      icon="mdi-check"
      :title="dialogTitle"
      dialog-class="notify-dialog"
      max-width="680"
      :isPersistent="true"
      data-test="modal-suspend-account"
    >
      <template #icon>
        <v-icon
          large
          color="error"
        >
          mdi-alert-circle-outline
        </v-icon>
      </template>
      <template #text>
        <p class="px-10">
          {{ dialogText }}<br>
        </p>
        <v-form
          id="suspensionReasonForm"
          ref="suspensionReasonForm"
        >
          <v-select
            v-if="isAccountStatusActive"
            v-model="selectedSuspensionReasonCode"
            class="px-10"
            filled
            label="Reason for Suspension"
            req
            :rules="suspensionSelectRules"
            :items="suspensionReasonCodes"
            item-text="desc"
            item-value="code"
            data-test="select-suspend-account-reason"
          />
        </v-form>
      </template>
      <template #actions>
        <v-btn
          large
          class="font-weight-bold white--text btn-dialog"
          :color="getDialogStatusButtonColor(currentOrganization.orgStatus)"
          data-test="btn-suspend-dialog"
          @click="confirmSuspendAccount()"
        >
          {{ isAccountStatusActive ? 'Suspend' : 'Unsuspend' }}
        </v-btn>
        <v-btn
          large
          depressed
          class="btn-dialog"
          data-test="btn-cancel-suspend-dialog"
          @click="closeSuspendAccountDialog()"
        >
          Cancel
        </v-btn>
      </template>
    </ModalDialog>
    <!-- Suspend Confirmation Dialog -->
    <ModalDialog
      ref="suspensionCompleteDialog"
      title="Account has been suspended"
      :text="suspensionCompleteDialogText"
      dialog-class="notify-dialog"
      max-width="680"
      :isPersistent="true"
      data-test="modal-suspension-complete"
    >
      <template #icon>
        <v-icon
          large
          color="primary"
        >
          mdi-check
        </v-icon>
      </template>
      <template #actions>
        <v-btn
          large
          depressed
          class="font-weight-bold white--text btn-dialog"
          data-test="btn-suspend-confirm-dialog"
          color="primary"
          @click="closeSuspensionCompleteDialog()"
        >
          OK
        </v-btn>
      </template>
    </ModalDialog>
  </v-container>
</template>

<script lang="ts">
import { AccessType, AccountStatus, Pages, Permission, Role, SuspensionReason } from '@/util/constants'
import { CreateRequestBody, OrgBusinessType } from '@/models/Organization'
import { computed, defineComponent, onBeforeUnmount, onMounted, ref } from '@vue/composition-api'
import { useAccount, useAccountChangeHandler } from '@/composables'
import AccountAccessType from '@/components/auth/account-settings/account-info/AccountAccessType.vue'
import AccountDetails from '@/components/auth/account-settings/account-info/AccountDetails.vue'
import AccountMailingAddress from '@/components/auth/account-settings/account-info/AccountMailingAddress.vue'
import { Address } from '@/models/address'
import LinkedBCOLBanner from '@/components/auth/common/LinkedBCOLBanner.vue'
import ModalDialog from '../../common/ModalDialog.vue'
import OrgAdminContact from '@/components/auth/account-settings/account-info/OrgAdminContact.vue'
import { useCodesStore } from '@/stores/codes'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  components: {
    OrgAdminContact,
    LinkedBCOLBanner,
    ModalDialog,
    AccountDetails,
    AccountMailingAddress,
    AccountAccessType
  },
  setup (props, { root }) {
    const codesStore = useCodesStore()
    const orgStore = useOrgStore()
    const userStore = useUserStore()

    const { setAccountChangedHandler, beforeDestroy } = useAccountChangeHandler()
    const {
      currentOrganization,
      currentOrgPaymentType,
      currentOrgAddress,
      permissions,
      getAccountFromSession,
      isPremiumAccount,
      anonAccount,
      isGovmAccount,
      isStaffAccount,
      isSbcStaffAccount
    } = useAccount()

    const suspensionReasonCodes = computed(() => codesStore.suspensionReasonCodes)
    const currentUser = computed(() => userStore.currentUser)
    const isBusinessAccount = computed(() => orgStore.isBusinessAccount)
    const dialogTitle = ref('')
    const dialogText = ref('')
    const selectedSuspensionReasonCode = ref('')
    const suspensionCompleteDialogText = ref('')
    const isSuspensionReasonFormValid = ref(false)
    const addressChanged = ref(false)
    const originalAddress = ref(null)
    const errorMessage = ref('')
    const warningMessage = ref('')
    const isBaseAddressValid = ref(false)
    const isCompleteAccountInfo = ref(true)
    const accountDetails = ref<OrgBusinessType>({})
    const isAddressViewOnly = ref(true)
    const isAccountInfoViewOnly = ref(true)
    const isAccessTypeViewOnly = ref(true)
    const baseAddress = ref(currentOrgAddress.value)

    const editAccountForm = ref(null)
    const mailingAddress = ref(null)
    const suspendAccountDialog = ref(null)
    const suspensionCompleteDialog = ref(null)
    const suspensionReasonForm = ref(null)

    const isStaff = computed(() => currentUser.value.roles.includes(Role.Staff))
    const isSuspendButtonVisible = computed(() => (
      (currentOrganization.value.statusCode === AccountStatus.ACTIVE ||
      currentOrganization.value.statusCode === AccountStatus.SUSPENDED) &&
      currentUser.value.roles.includes(Role.StaffSuspendAccounts)
    ))
    const isDeactivateButtonVisible = computed(() => currentOrganization.value?.statusCode !== AccountStatus.INACTIVE)
    const editAccountUrl = Pages.EDIT_ACCOUNT_TYPE
    const canChangeAccessType = computed(() => currentUser.value.roles.includes(Role.StaffManageAccounts))
    const isAddressEditable = computed(() => [Permission.CHANGE_ADDRESS].some(per => permissions.value.includes(per)))
    const isAdminContactViewable = computed(() => [Permission.VIEW_ADMIN_CONTACT].some(per => permissions.value.includes(per)))
    const isAccountStatusActive = computed(() => currentOrganization.value.statusCode === AccountStatus.ACTIVE)
    const accountType = computed(() => {
      if (isStaffAccount.value) {
        return 'BC Registry Staff'
      } else if (isSbcStaffAccount.value) {
        return 'SBC Staff'
      }
      return isPremiumAccount.value ? 'Premium' : 'Basic'
    })
    const isBusinessInfoIncomplete = computed(() => (
      isBusinessAccount.value && !(accountDetails.value?.businessSize && accountDetails.value?.businessType)
    ))
    const isAddressInfoIncomplete = computed(() => (
      currentOrgAddress.value ? Object.keys(currentOrgAddress.value).length === 0 : true
    ))
    const nameChangeNotAllowed = computed(() => (anonAccount.value || isGovmAccount.value))

    const suspensionSelectRules = [
      v => !!v || 'A reason for suspension is required'
    ]

    const setAccountDetails = () => {
      accountDetails.value = {
        ...accountDetails.value,
        name: currentOrganization.value?.name || '',
        branchName: currentOrganization.value?.branchName || '',
        businessType: currentOrganization.value.businessType || '',
        businessSize: currentOrganization.value?.businessSize || ''
      }
    }

    const getWarningMessage = (condition: boolean) => condition
      ? 'This account info is incomplete. You will not be able to proceed until an account administrator ' +
          'entered the missing information for this account.'
      : 'Your account info is incomplete. Please update any missing account details or address.'

    const setup = async () => {
      setAccountDetails()
      await orgStore.syncAddress()
      if (!anonAccount.value) {
        originalAddress.value = currentOrgAddress.value
        if (isBusinessInfoIncomplete.value || isAddressInfoIncomplete.value) {
          isCompleteAccountInfo.value = false
          warningMessage.value = getWarningMessage(isBusinessInfoIncomplete.value ? nameChangeNotAllowed.value : !isAddressEditable.value)
        } else {
          isCompleteAccountInfo.value = true
          warningMessage.value = ''
        }
      } else {
        baseAddress.value = null
      }
    }

    const viewOnlyMode = async (details) => {
      const { component, mode } = details
      if (component === 'address') {
        isAddressViewOnly.value = mode
      }
      if (component === 'account') {
        isAccountInfoViewOnly.value = mode
      }
      if (component === 'accessType') {
        if (!mode) {
          await orgStore.getOrgPayments()
        }
        isAccessTypeViewOnly.value = mode
      }
    }

    const updateDetails = async () => {
      errorMessage.value = ''
      const { branchName, businessSize, businessType, name, isBusinessAccount } = accountDetails.value

      let createRequestBody: CreateRequestBody = {}
      if (baseAddress.value && addressChanged.value && JSON.stringify(originalAddress.value) !== JSON.stringify(currentOrgAddress.value)) {
        createRequestBody.mailingAddress = { ...baseAddress.value }
      }
      if (name !== currentOrganization.value.name) {
        createRequestBody.name = name
      }
      if (branchName !== currentOrganization.value.branchName) {
        createRequestBody.branchName = branchName
      }
      // need to check type since we need to send false also
      // eslint-disable-next-line valid-typeof
      if (typeof isBusinessAccount !== undefined) {
        createRequestBody.isBusinessAccount = isBusinessAccount
      }
      if (isBusinessAccount && 'businessSize' in accountDetails.value && businessSize !== null) {
        if (currentOrganization.value.businessSize !== businessSize) {
          createRequestBody.businessSize = businessSize
        }
      }
      if (isBusinessAccount && 'businessType' in accountDetails.value && businessType !== null) {
        if (currentOrganization.value.businessType !== businessType) {
          createRequestBody.businessType = businessType
        }
      }

      try {
        await orgStore.updateOrg(createRequestBody)
        if (!(isStaff.value && !isStaffAccount.value)) root.$store.commit('updateHeader')
        addressChanged.value = false
        originalAddress.value = currentOrgAddress.value
        if (!isBusinessInfoIncomplete.value && !isAddressInfoIncomplete.value) {
          isCompleteAccountInfo.value = true
          warningMessage.value = ''
        }
        viewOnlyMode({ component: 'address', mode: true })
        viewOnlyMode({ component: 'account', mode: true })
      } catch (err) {
        switch (err.response.status) {
          case 409:
            errorMessage.value = 'An account with this name already exists. Try a different account name.'
            break
          default:
            errorMessage.value = 'An error occurred while attempting to update your account.'
        }
      }
    }

    const resetAddress = () => {
      baseAddress.value = originalAddress.value
      viewOnlyMode('address')
    }

    const getStatusColor = (status) => {
      switch (status) {
        case AccountStatus.NSF_SUSPENDED:
        case AccountStatus.SUSPENDED:
        case AccountStatus.INACTIVE:
          return 'error'
        case AccountStatus.ACTIVE:
          return 'green'
        default:
          return 'primary'
      }
    }

    const getDialogStatusButtonColor = (status) => {
      switch (status) {
        case AccountStatus.NSF_SUSPENDED:
        case AccountStatus.SUSPENDED:
          return 'green'
        case AccountStatus.ACTIVE:
          return 'error'
        default:
          return 'primary'
      }
    }

    const getStatusText = (status) => {
      switch (status) {
        case AccountStatus.NSF_SUSPENDED:
          return SuspensionReason.NSF_SUSPENDED
        case AccountStatus.SUSPENDED:
          return SuspensionReason.SUSPENDED
        default:
          return status
      }
    }

    const updateAndSaveAccountDetails = (accountDetails) => {
      accountDetails.value = accountDetails
      updateDetails()
    }

    const updateAndSaveAccessTypeDetails = async (accessType: string) => {
      await orgStore.updateOrganizationAccessType(accessType, currentOrganization.value.id, true)
      if (accessType === AccessType.REGULAR) {
        await orgStore.removeOrgAccountFees(currentOrganization.value.id)
      }
      viewOnlyMode({ component: 'accessType', mode: true })
    }

    const showSuspendAccountDialog = (status) => {
      if (status === AccountStatus.ACTIVE) {
        dialogTitle.value = 'Suspend Account'
        dialogText.value = 'suspendAccountText'
      } else {
        dialogTitle.value = 'Unsuspend Account'
        dialogText.value = 'unsuspendAccountText'
      }
      suspendAccountDialog.value.open()
    }

    const confirmSuspendAccount = async () => {
      isSuspensionReasonFormValid.value = suspensionReasonForm.value?.validate()
      if (isSuspensionReasonFormValid.value) {
        await orgStore.suspendOrganization(selectedSuspensionReasonCode.value)
        suspendAccountDialog.value.close()
        if (currentOrganization.value.statusCode === AccountStatus.SUSPENDED) {
          suspensionCompleteDialogText.value = `The account ${currentOrganization.value.name} has been suspended.`
          suspensionCompleteDialog.value.open()
        }
      }
    }

    const closeSuspendAccountDialog = () => {
      suspendAccountDialog.value.close()
    }

    const closeSuspensionCompleteDialog = () => {
      suspensionCompleteDialog.value.close()
    }

    const checkBaseAddressValidity = (isValid) => {
      isBaseAddressValid.value = !!isValid
    }

    const updateAddress = (address: Address) => {
      addressChanged.value = true
      orgStore.setCurrentOrganizationAddress(address)
    }

    onMounted(async () => {
      const accountSettings = getAccountFromSession()
      console.log("accountSettings", accountSettings)
      await orgStore.syncOrganization(accountSettings?.id)
      setAccountChangedHandler(setup)
      await setup()
    })

    onBeforeUnmount(() => { beforeDestroy() })

    return {
      suspensionReasonCodes,
      currentOrganization,
      currentOrgAddress,
      permissions,
      currentOrgPaymentType,
      currentUser,
      isBusinessAccount,
      dialogTitle,
      dialogText,
      selectedSuspensionReasonCode,
      suspensionCompleteDialogText,
      isSuspensionReasonFormValid,
      addressChanged,
      originalAddress,
      errorMessage,
      warningMessage,
      isBaseAddressValid,
      isCompleteAccountInfo,
      accountDetails,
      isAddressViewOnly,
      isAccountInfoViewOnly,
      isAccessTypeViewOnly,
      isStaff,
      isSuspendButtonVisible,
      isDeactivateButtonVisible,
      editAccountUrl,
      canChangeAccessType,
      suspensionSelectRules,
      isAddressEditable,
      isAdminContactViewable,
      isAccountStatusActive,
      isBusinessInfoIncomplete,
      isAddressInfoIncomplete,
      accountType,
      baseAddress,
      nameChangeNotAllowed,
      anonAccount,
      isGovmAccount,
      isStaffAccount,
      editAccountForm,
      mailingAddress,
      suspendAccountDialog,
      suspensionCompleteDialog,
      suspensionReasonForm,
      setAccountDetails,
      setup,
      viewOnlyMode,
      updateDetails,
      resetAddress,
      getStatusColor,
      getDialogStatusButtonColor,
      getStatusText,
      updateAndSaveAccountDetails,
      updateAndSaveAccessTypeDetails,
      showSuspendAccountDialog,
      confirmSuspendAccount,
      closeSuspendAccountDialog,
      closeSuspensionCompleteDialog,
      checkBaseAddressValidity,
      updateAddress
    }
  }
})
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.v-application p {
  margin-bottom: 3rem;
}

.nv-list {
  margin: 0;
  padding: 0;
  list-style-type: none;
}

.nv-list-item {
  display: flex;
  vertical-align: top;

  .name,
  .value {
    display: inline-block;
    vertical-align: top;
  }

  .name {
    flex: 0 0 auto;
    width: 12rem;
  }

  .value {
    flex: 1 1 auto;
  }
}

.v-list--dense .v-list-item .v-list-item__title {
  font-weight: 700;
}

.form__btns {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  align-items: center;
  margin-top: 2rem;

  .v-btn {
    width: 6rem;
  }
}
// .form__btns > *:first-child {
//   margin-right: auto;
// }

.account-nav-container {
  height: 100%;
  border-right: 1px solid #eeeeee;
}

.header-container {
  display: flex;
  flex-direction: row;
}

// BC Online Account Information
.bcol-acc__name {
  font-size: 1.125rem;
  font-weight: 700;
}

.bcol-acc__meta {
  margin: 0;
  padding: 0;
  list-style-type: none;

  li {
    position: relative;
    display: inline-block;
  }

  li + li {
    &:before {
      content: ' | ';
      display: inline-block;
      position: relative;
      top: -2px;
      left: 2px;
      width: 2rem;
      vertical-align: top;
      text-align: center;
    }
  }
}

.change-account-link {
  font-size: 0.875rem;
}

.value-column {
  display: flex;
  flex-direction: column;
}

.value-column > div {
  margin-bottom: 1rem;
}

.suspend-account-btn {
  margin-left: 0 !important;
  height: 2.1em;
  width: 10.9375em;
}

.btn-dialog {
  height: 2.75em;
  width: 6.25em;
}
.deactivate-btn {
  height: auto !important;
  padding: 0.2rem 0.2rem !important;
  font-size: 1rem !important;
  text-decoration: underline;
  margin-right: auto;
}
.custom-warning {
  border-radius: 4px;
  border: 1px solid $BCgovGold5 !important;
  background: $BCgovGold0 !important;
  color: $gray7;
}
::v-deep {
  .custom-warning .v-icon {
    color: $app-alert-orange !important;
  }
}
</style>
