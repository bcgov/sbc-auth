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

        <template v-if="baseAddress">
          <div v-can:VIEW_ADDRESS.hide>
            <v-divider class="mt-3 mb-5" />
            <!-- TODO: can use v-can instead of v-if if all user with change permisson have view also -->
            <AccountMailingAddress
              ref="mailingAddress"
              :baseAddress="baseAddress"
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
              v-can:DEACTIVATE_ACCOUNT.hide
              text
              color="primary"
              class="deactivate-btn font-weight-bold"
              data-test="deactivate-btn"
              to="/account-deactivate"
              @click="learnMoreDialog = true"
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
import {
  AccountStatus,
  Pages,
  Permission,
  Role,
  SessionStorageKeys
} from '@/util/constants'
import { Component, Mixins } from 'vue-property-decorator'
import {
  CreateRequestBody,
  OrgBusinessType,
  Organization
} from '@/models/Organization'

import AccountAccessType from '@/components/auth/account-settings/account-info/AccountAccessType.vue'
import AccountBusinessTypePicker from '@/components/auth/common/AccountBusinessTypePicker.vue'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import AccountDetails from '@/components/auth/account-settings/account-info/AccountDetails.vue'
import AccountMailingAddress from '@/components/auth/account-settings/account-info/AccountMailingAddress.vue'
import AccountMixin from '@/components/auth/mixins/AccountMixin.vue'
import { AccountSettings } from '@/models/account-settings'
import { Address } from '@/models/address'
import { Code } from '@/models/Code'
import ConfigHelper from '@/util/config-helper'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import LinkedBCOLBanner from '@/components/auth/common/LinkedBCOLBanner.vue'
import ModalDialog from '../../common/ModalDialog.vue'
import OrgAdminContact from '@/components/auth/account-settings/account-info/OrgAdminContact.vue'

import { namespace } from 'vuex-class'

const CodesModule = namespace('codes')
const OrgModule = namespace('org')
const userModule = namespace('user')

@Component({
  components: {
    OrgAdminContact,
    LinkedBCOLBanner,
    ModalDialog,
    AccountBusinessTypePicker,
    AccountDetails,
    AccountMailingAddress,
    AccountAccessType
  }
})
export default class AccountInfo extends Mixins(
  AccountChangeMixin,
  AccountMixin
) {
  @CodesModule.State('suspensionReasonCodes')
  private suspensionReasonCodes!: Code[]
  @OrgModule.State('currentMembership') public currentMembership!: Organization
  @OrgModule.State('currentOrgAddress') public currentOrgAddress!: Address
  @OrgModule.State('permissions') public permissions!: string[]
  @OrgModule.State('currentOrgPaymentType') public currentOrgPaymentType!: string
  @userModule.State('currentUser') public currentUser!: KCUserProfile

  @OrgModule.Getter('isBusinessAccount') public isBusinessAccount!: boolean
  @OrgModule.Mutation('setCurrentOrganizationAddress')
  public setCurrentOrganizationAddress!: (address: Address) => void

  @OrgModule.Action('updateOrg') public updateOrg!: (
    requestBody: CreateRequestBody
  ) => Promise<Organization>

  @OrgModule.Action('syncAddress') syncAddress!: () => Address
  @OrgModule.Action('getOrgPayments') getOrgPayments!: () => any
  @OrgModule.Action('updateOrganizationAccessType') updateOrganizationAccessType!: (
    accessType: string
  ) => Promise<Organization>

  @OrgModule.Action('syncOrganization') syncOrganization!: (
    currentAccount: number
  ) => Promise<Organization>
  @OrgModule.Action('suspendOrganization') suspendOrganization!: (
    selectedSuspensionReasonCode: string
  ) => Promise<Organization>

  private dialogTitle: string = ''
  private dialogText: string = ''
  private selectedSuspensionReasonCode: string = ''
  private suspensionCompleteDialogText: string = ''
  private isSuspensionReasonFormValid: boolean = false
  private addressChanged = false
  // private readonly isBusinessAccount!: boolean
  private originalAddress: Address // store the original address..do not modify it afterwards

  private errorMessage: string = ''

  private isBaseAddressValid: boolean = false
  private isCompleteAccountInfo = true
  private accountDetails: OrgBusinessType = {}
  public isAddressViewOnly = true
  public isAccountInfoViewOnly = true
  public isAccessTypeViewOnly = true

  $refs: {
    editAccountForm: HTMLFormElement
    mailingAddress: HTMLFormElement
    suspendAccountDialog: ModalDialog
    suspensionCompleteDialog: ModalDialog
    suspensionReasonForm: HTMLFormElement
    accountBusinessTypePickerRef: HTMLFormElement
  }

  private setAccountDetails () {
    // Create a new object, to trigger the watch in AccountDetails.
    this.accountDetails = {
      ...this.accountDetails,
      name: this.currentOrganization?.name || '',
      branchName: this.currentOrganization?.branchName || '',
      businessType: this.currentOrganization.businessType || '',
      businessSize: this.currentOrganization?.businessSize || ''
    }
  }
  private async setup () {
    this.setAccountDetails()
    await this.syncAddress()

    // show this part only account is not anon
    if (!this.anonAccount) {
      this.originalAddress = this.currentOrgAddress
      if (Object.keys(this.currentOrgAddress).length === 0) {
        this.isCompleteAccountInfo = false
        this.errorMessage = this.isAddressEditable
          ? 'Your account info is incomplete. Please enter your address in order to proceed.'
          : 'This accounts profile is incomplete. You will not be able to proceed until an account administrator entered the missing information for this account.'
        this.$refs.editAccountForm?.validate() // validate form fields and show error message
        // SBTODO create a method in child comp
        this.$refs.mailingAddress?.triggerValidate() // validate form fields and show error message for address component from sbc-common-comp
      }
    } else {
      // inorder to hide the address if not premium account
      this.baseAddress = null
    }
  }

  private get isStaff (): boolean {
    return this.currentUser.roles.includes(Role.Staff)
  }
  // update account detaisl from child component
  public updateAndSaveAccountDetails (accountDetails) {
    this.accountDetails = accountDetails
    // once we got the values , set to values and save
    this.updateDetails()
  }

  // update account access type from child component
  public async updateAndSaveAccessTypeDetails (accessType: string) {
    await this.updateOrganizationAccessType(accessType)
    this.viewOnlyMode({ component: 'accessType', mode: true })
  }

  private get isSuspendButtonVisible (): boolean {
    return (
      (this.currentOrganization.statusCode === AccountStatus.ACTIVE ||
        this.currentOrganization.statusCode === AccountStatus.SUSPENDED) &&
      this.currentUser.roles.includes(Role.StaffSuspendAccounts)
    )
  }

  get editAccountUrl () {
    return Pages.EDIT_ACCOUNT_TYPE
  }

  get canChangeAccessType (): boolean {
    return this.currentUser.roles.includes(Role.StaffManageAccounts)
  }

  private suspensionSelectRules = [
    v => !!v || 'A reason for suspension is required'
  ]

  private async mounted () {
    const accountSettings = this.getAccountFromSession()
    await this.syncOrganization(accountSettings.id)
    this.setAccountChangedHandler(this.setup)
    await this.setup()
  }

  private get baseAddress () {
    return this.currentOrgAddress
  }
  private get nameChangeNotAllowed () {
    return (this.anonAccount || this.isGovmAccount)
  }

  resetAddress () {
    this.baseAddress = this.originalAddress
    this.viewOnlyMode('address')
  }
  // use same funtion to toggle both account info and mailer view mode
  public async viewOnlyMode (details) {
    const { component, mode } = details
    if (component === 'address') {
      this.isAddressViewOnly = mode
    }
    if (component === 'account') {
      this.isAccountInfoViewOnly = mode
    }
    if (component === 'accessType') {
      // Get org payment methods if it is edit mode
      if (!mode) {
        await this.getOrgPayments()
      }
      this.isAccessTypeViewOnly = mode
    }
  }

  private set baseAddress (address) {
    this.setCurrentOrganizationAddress(address)
  }

  async beforeRouteLeave (to, from, next) {
    if (!this.isAddressEditable || this.isCompleteAccountInfo) {
      next()
    } else {
      // eslint-disable-next-line no-console
      console.log('account info incomplete.blocking navigation')
    }
  }

  private updateAddress (address: Address) {
    this.addressChanged = true
    this.setCurrentOrganizationAddress(address)
  }

  private async showSuspendAccountDialog (status) {
    if (status === AccountStatus.ACTIVE) {
      this.dialogTitle = 'Suspend Account'
      this.dialogText = this.$t('suspendAccountText').toString()
    } else {
      this.dialogTitle = 'Unsuspend Account'
      this.dialogText = this.$t('unsuspendAccountText').toString()
    }
    this.$refs.suspendAccountDialog.open()
  }

  private async confirmSuspendAccount (): Promise<void> {
    this.isSuspensionReasonFormValid = this.$refs.suspensionReasonForm?.validate()
    if (this.isSuspensionReasonFormValid) {
      await this.suspendOrganization(this.selectedSuspensionReasonCode)
      this.$refs.suspendAccountDialog.close()
      if (this.currentOrganization.statusCode === AccountStatus.SUSPENDED) {
        this.suspensionCompleteDialogText = `The account ${this.currentOrganization.name} has been suspended.`
        this.$refs.suspensionCompleteDialog.open()
      }
    }
  }

  private closeSuspendAccountDialog () {
    this.$refs.suspendAccountDialog.close()
  }

  private closeSuspensionCompleteDialog () {
    this.$refs.suspensionCompleteDialog.close()
  }

  protected getAccountFromSession (): AccountSettings {
    return JSON.parse(
      ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccount || '{}')
    )
  }

  private async updateDetails () {
    this.errorMessage = ''
    const { branchName, businessSize, businessType, name, isBusinessAccount } = this.accountDetails

    let createRequestBody: CreateRequestBody = {}
    if (
      this.baseAddress &&
      this.addressChanged &&
      JSON.stringify(this.originalAddress) !==
        JSON.stringify(this.currentOrgAddress)
    ) {
      createRequestBody.mailingAddress = { ...this.baseAddress }
    }
    if (name !== this.currentOrganization.name) {
      createRequestBody.name = name
    }
    if (branchName !== this.currentOrganization.branchName) {
      createRequestBody.branchName = branchName
    }
    // need to check type since we need to send false also
    // eslint-disable-next-line valid-typeof
    if (typeof isBusinessAccount !== undefined) {
      createRequestBody.isBusinessAccount = isBusinessAccount
    }
    if (this.isBusinessAccount && this.accountDetails) {
      if (this.currentOrganization.businessSize !== businessSize) {
        createRequestBody.businessSize = businessSize
      }
      if (this.currentOrganization.businessType !== businessType) {
        createRequestBody.businessType = businessType
      }
    }

    try {
      await this.updateOrg(createRequestBody)
      // FUTURE: change 'staff view other account' flow so it doesn't need to fake load the other account globally
      // if staff updating a user account don't reload header -- causes staff account to get loaded in
      if (!(this.isStaff && !this.isStaffAccount)) this.$store.commit('updateHeader')
      this.addressChanged = false
      if (this.baseAddress) {
        this.isCompleteAccountInfo = true
      }
      this.viewOnlyMode({ component: 'address', mode: true })
      this.viewOnlyMode({ component: 'account', mode: true })
    } catch (err) {
      switch (err.response.status) {
        case 409:
          this.errorMessage =
            'An account with this name already exists. Try a different account name.'
          break
        case 400:
          this.errorMessage = 'Invalid account name'
          break
        default:
          this.errorMessage =
            'An error occurred while attempting to update your account.'
      }
    }
  }

  private checkBaseAddressValidity (isValid) {
    this.isBaseAddressValid = !!isValid
  }

  get isAddressEditable (): boolean {
    return [Permission.CHANGE_ADDRESS].some(per =>
      this.permissions.includes(per)
    )
  }

  // SBTODO May be v-can
  get isAdminContactViewable (): boolean {
    return [Permission.VIEW_ADMIN_CONTACT].some(per =>
      this.permissions.includes(per)
    )
  }

  get isAccountStatusActive (): boolean {
    return this.currentOrganization.statusCode === AccountStatus.ACTIVE
  }

  private getStatusColor (status) {
    switch (status) {
      case AccountStatus.NSF_SUSPENDED:
      case AccountStatus.SUSPENDED:
        return 'error'
      case AccountStatus.ACTIVE:
        return 'green'
      default:
        return 'primary'
    }
  }

  private getDialogStatusButtonColor (status) {
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

  private getStatusText (status) {
    switch (status) {
      case AccountStatus.NSF_SUSPENDED:
        return 'NSF SUSPENDED'
      case AccountStatus.SUSPENDED:
        return 'SUSPENDED'
      default:
        return status
    }
  }

  get accountType () {
    if (this.isStaffAccount) {
      return 'BC Registry Staff'
    } else if (this.isSbcStaffAccount) {
      return 'SBC Staff'
    }
    return this.isPremiumAccount ? 'Premium' : 'Basic'
  }
}
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
</style>
