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

        <div v-show="true">
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
            <template v-if="accountType !== OrgAccountTypes.PREMIUM">
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
            </template>
          </div>
          <AccountAccessType
            :organization="currentOrganization"
            :viewOnlyMode="isAccessTypeViewOnly"
            :currentOrgPaymentType="currentOrgPaymentType"
            :canChangeAccessType="canChangeAccessType"
            @update:viewOnlyMode="viewOnlyMode"
            @update:updateAndSaveAccessTypeDetails="updateAndSaveAccessTypeDetails"
          />
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
            <OrgAdminContact :orgId="orgId" />
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
              @update:updateDetails="updateOrgMailingAddress"
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
          {{ $t(dialogText) }}<br>
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
import { AccessType, AccountStatus, Permission, Role, SuspensionReason } from '@/util/constants'
import { CreateRequestBody, OrgAccountTypes, OrgBusinessType } from '@/models/Organization'
import { computed, defineComponent, onBeforeUnmount, onMounted, reactive, toRefs } from '@vue/composition-api'
import { useAccount, useAccountChangeHandler } from '@/composables'
import AccountAccessType from '@/components/auth/account-settings/account-info/AccountAccessType.vue'
import AccountDetails from '@/components/auth/account-settings/account-info/AccountDetails.vue'
import AccountMailingAddress from '@/components/auth/account-settings/account-info/AccountMailingAddress.vue'
import { Address } from '@/models/address'
import ModalDialog from '../../common/ModalDialog.vue'
import OrgAdminContact from '@/components/auth/account-settings/account-info/OrgAdminContact.vue'
import { useAppStore } from '@/stores/app'
import { useCodesStore } from '@/stores/codes'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  components: {
    OrgAdminContact,
    ModalDialog,
    AccountDetails,
    AccountMailingAddress,
    AccountAccessType
  },
  props: ['orgId'],
  setup () {
    const codesStore = useCodesStore()
    const orgStore = useOrgStore()
    const userStore = useUserStore()

    const { setAccountChangedHandler, beforeDestroy } = useAccountChangeHandler()
    const {
      currentOrganization,
      currentOrgPaymentType,
      currentOrgAddress,
      permissions,
      isGovmAccount,
      isStaffAccount,
      isSbcStaffAccount
    } = useAccount()

    const state = reactive({
      dialogTitle: '',
      dialogText: '',
      selectedSuspensionReasonCode: '',
      suspensionCompleteDialogText: '',
      isSuspensionReasonFormValid: false,
      addressChanged: false,
      originalAddress: null,
      errorMessage: '',
      warningMessage: '',
      isBaseAddressValid: false,
      isCompleteAccountInfo: true,
      accountDetails: {} as OrgBusinessType,
      isAddressViewOnly: true,
      isAccountInfoViewOnly: true,
      isAccessTypeViewOnly: true,
      editAccountForm: null,
      mailingAddress: null,
      suspendAccountDialog: null,
      suspensionCompleteDialog: null,
      suspensionReasonForm: null,

      suspensionReasonCodes: computed(() => codesStore.suspensionReasonCodes),
      currentUser: computed(() => userStore.currentUser),
      isBusinessAccount: computed(() => orgStore.isBusinessAccount),
      baseAddress: computed(() => currentOrgAddress.value),

      isStaff: computed(() => userStore.currentUser.roles.includes(Role.Staff)) || userStore.currentUser.roles.includes(Role.ExternalStaffReadonly),
      isSuspendButtonVisible: computed(() => (
        (currentOrganization.value.statusCode === AccountStatus.ACTIVE ||
        currentOrganization.value.statusCode === AccountStatus.SUSPENDED) &&
        userStore.currentUser.roles.includes(Role.StaffSuspendAccounts)
      )),
      isDeactivateButtonVisible: computed(() => currentOrganization.value?.statusCode !== AccountStatus.INACTIVE),
      canChangeAccessType: computed(() => (
        userStore.currentUser.roles.includes(Role.StaffManageAccounts)
      )),
      isAdminContactViewable: computed(() => [Permission.VIEW_ADMIN_CONTACT].some(per => permissions.value.includes(per))),
      isAccountStatusActive: computed(() => currentOrganization.value.statusCode === AccountStatus.ACTIVE),
      accountType: computed(() => {
        if (isStaffAccount.value) {
          return 'BC Registry Staff'
        } else if (isSbcStaffAccount.value) {
          return 'SBC Staff'
        }
        return 'Premium'
      }),
      isAddressInfoIncomplete: computed(() => (
        currentOrgAddress.value ? Object.keys(currentOrgAddress.value).length === 0 : true
      )),
      nameChangeNotAllowed: computed(() => (isGovmAccount.value)) &&
      userStore.currentUser.roles.includes(Role.ExternalStaffReadonly)
    })

    const suspensionSelectRules = [
      v => !!v || 'A reason for suspension is required'
    ]

    const setAccountDetails = () => {
      state.accountDetails = {
        ...state.accountDetails,
        name: currentOrganization.value?.name || '',
        branchName: currentOrganization.value?.branchName || '',
        businessType: currentOrganization.value.businessType || '',
        businessSize: currentOrganization.value?.businessSize || ''
      }
    }

    const isBusinessInfoIncomplete = computed(() => (
      state.isBusinessAccount && !(state.accountDetails?.businessSize && state.accountDetails?.businessType)
    ))

    const warningMessage = 'Your account info is incomplete. Please update any missing account details or address.'

    const setup = async () => {
      setAccountDetails()
      await orgStore.syncAddress()
      state.originalAddress = currentOrgAddress.value
      if (isBusinessInfoIncomplete.value || state.isAddressInfoIncomplete) {
        state.isCompleteAccountInfo = false
        state.warningMessage = warningMessage
      } else {
        state.isCompleteAccountInfo = true
        state.warningMessage = ''
      }
    }

    const viewOnlyMode = async (details) => {
      const { component, mode } = details
      if (component === 'address') {
        state.isAddressViewOnly = mode
      }
      if (component === 'account') {
        state.isAccountInfoViewOnly = mode
      }
      if (component === 'accessType') {
        if (!mode) {
          await orgStore.getOrgPayments()
        }
        state.isAccessTypeViewOnly = mode
      }
    }

    const updateDetails = async () => {
      state.errorMessage = ''
      const { branchName, businessSize, businessType, name, isBusinessAccount } = state.accountDetails

      let createRequestBody: CreateRequestBody = {}
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
      if (isBusinessAccount && 'businessSize' in state.accountDetails && businessSize !== null) {
        if (currentOrganization.value.businessSize !== businessSize) {
          createRequestBody.businessSize = businessSize
        }
      }
      if (isBusinessAccount && 'businessType' in state.accountDetails && businessType !== null) {
        if (currentOrganization.value.businessType !== businessType) {
          createRequestBody.businessType = businessType
        }
      }

      try {
        await orgStore.updateOrg(createRequestBody)
        if (!(state.isStaff && !isStaffAccount.value)) useAppStore().updateHeader()
        if (!isBusinessInfoIncomplete.value && !state.isAddressInfoIncomplete) {
          state.isCompleteAccountInfo = true
          state.warningMessage = ''
        }
        viewOnlyMode({ component: 'account', mode: true })
      } catch (err) {
        switch (err.response.status) {
          case 409:
            state.errorMessage = 'An account with this name already exists. Try a different account name.'
            break
          default:
            state.errorMessage = 'An error occurred while attempting to update your account.'
        }
      }
    }

    async function updateOrgMailingAddress () {
      state.errorMessage = ''

      let createRequestBody: CreateRequestBody = {}
      if (state.baseAddress && state.addressChanged && JSON.stringify(state.originalAddress) !== JSON.stringify(currentOrgAddress.value)) {
        createRequestBody.mailingAddress = { ...state.baseAddress }
      }

      try {
        await orgStore.updateOrgMailingAddress(createRequestBody)
        if (!(state.isStaff && !isStaffAccount.value)) useAppStore().updateHeader()
        state.addressChanged = false
        state.originalAddress = currentOrgAddress.value
        if (!isBusinessInfoIncomplete.value && !state.isAddressInfoIncomplete) {
          state.isCompleteAccountInfo = true
          state.warningMessage = ''
        }
        viewOnlyMode({ component: 'address', mode: true })
      } catch (err) {
        state.errorMessage = 'An error occurred while attempting to update your mailing address.'
      }
    }

    const resetAddress = () => {
      state.baseAddress = state.originalAddress
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
      state.accountDetails = accountDetails
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
        state.dialogTitle = 'Suspend Account'
        state.dialogText = 'suspendAccountText'
      } else {
        state.dialogTitle = 'Unsuspend Account'
        state.dialogText = 'unsuspendAccountText'
      }
      state.suspendAccountDialog.open()
    }

    const confirmSuspendAccount = async () => {
      state.isSuspensionReasonFormValid = state.suspensionReasonForm?.validate()
      if (state.isSuspensionReasonFormValid) {
        await orgStore.suspendOrganization(state.selectedSuspensionReasonCode)
        state.suspendAccountDialog.close()
        if (currentOrganization.value.statusCode === AccountStatus.SUSPENDED) {
          state.suspensionCompleteDialogText = `The account ${currentOrganization.value.name} has been suspended.`
          state.suspensionCompleteDialog.open()
        }
      }
    }

    const closeSuspendAccountDialog = () => {
      state.suspendAccountDialog.close()
    }

    const closeSuspensionCompleteDialog = () => {
      state.suspensionCompleteDialog.close()
    }

    const checkBaseAddressValidity = (isValid) => {
      state.isBaseAddressValid = !!isValid
    }

    const updateAddress = (address: Address) => {
      state.addressChanged = true
      orgStore.setCurrentOrganizationAddress(address)
    }

    onMounted(async () => {
      setAccountChangedHandler(setup)
      await setup()
    })

    onBeforeUnmount(() => { beforeDestroy() })

    return {
      ...toRefs(state),
      currentOrganization,
      currentOrgAddress,
      permissions,
      currentOrgPaymentType,
      suspensionSelectRules,
      isBusinessInfoIncomplete,
      isGovmAccount,
      isStaffAccount,
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
      updateAddress,
      updateOrgMailingAddress,
      OrgAccountTypes
    }
  }
})
</script>

<style lang="scss" scoped>
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
