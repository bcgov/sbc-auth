<template>
  <v-container>
    <header class="view-header mb-9">
      <h2 class="view-header__title">Account Info</h2>
    </header>
    <div>
      <v-form ref="editAccountForm">
        <v-alert type="error" class="mb-6" v-show="errorMessage">
          {{ errorMessage }}
        </v-alert>

        <div v-can:VIEW_ACCOUNT.hide>
          <div class="nv-list-item mb-10">
            <div class="name" id="accountName">Account Name</div>
            <div class="value" aria-labelledby="accountName">
              <div class="value__title">{{ currentOrganization.name }}</div>
            </div>
          </div>
        </div>

        <template v-show="!anonAccount">
          <div v-if="isStaff" class="nv-list-item mb-10">
            <div class="name" id="accountStatusStaff">Account Status</div>
            <div class="value-column">
               <div class="value" aria-labelledby="accountStatusStaff">
                <v-chip
                  small
                  label
                  class="font-weight-bold white--text"
                  :color="getStatusColor(currentOrganization.orgStatus)"
                  data-test='chip-account-status'
                >
                  {{ getStatusText(currentOrganization.orgStatus) }}
                </v-chip>
              </div>
              <v-btn
                large
                aria-label="Suspend Account"
                title="Suspend Account"
                class="suspend-account-btn mx-1 mb-3"
                @click="showSuspendAccountDialog(currentOrganization.orgStatus)"
                data-test='btn-suspend-account'
                v-if="isSuspendButtonVisible"
              >
                {{ isAccountStatusActive ? 'Suspend Account' : 'Unsuspend Account' }}
              </v-btn>
            </div>
          </div>
          <div class="nv-list-item mb-10">
            <div class="name" id="accountType">Account Type</div>
            <div class="value" aria-labelledby="accountType">
              <div class="value__title">{{ isPremiumAccount ? 'Premium' : 'Basic' }}</div>
              <div v-can:CHANGE_ACCOUNT_TYPE.hide v-if="enableUpgradeDowngrade">
                <router-link :to="editAccountUrl" v-can:CHANGE_ACCOUNT_TYPE.hide >Change account type</router-link>
              </div>
            </div>
          </div>
          <div class="nv-list-item mb-10" v-if="currentOrganization.bcolAccountDetails">
            <div class="name mt-3" id="accountName">Linked BC Online Account Details</div>
            <div class="value">
              <LinkedBCOLBanner
                :bcolAccountName="currentOrganization.bcolAccountName"
                :bcolAccountDetails="currentOrganization.bcolAccountDetails"
              ></LinkedBCOLBanner>
            </div>
          </div>
        </template>

        <div class="nv-list-item mb-10" v-if="isAdminContactViewable">
          <div class="name" id="adminContact">Account Contact</div>
          <div class="value" aria-labelledby="adminContact">
            <OrgAdminContact></OrgAdminContact>
          </div>
        </div>

        <div class="nv-list-item" v-can:CHANGE_ORG_NAME.disable>
          <div class="name">
            Account Details
          </div>
          <div class="value">
            <v-text-field
            filled
            clearable
            required
            label="Account Name"
            :rules="accountNameRules"
            v-can:CHANGE_ORG_NAME.disable
            :disabled="!canChangeAccountName()"
            v-model="orgName"
            v-on:keydown="enableBtn()"
            >
            </v-text-field>
          </div>
        </div>

        <div class="nv-list-item" v-if="(isAddressEditable || isAddressViewable)">
          <!-- template warpper is required here inorder to keep the placement of divs correctly(to resolve flickering issue when updating the address) -->
          <template v-if="baseAddress">
            <div class="name">
              Mailing Address
            </div>
            <div class="value">
              <base-address-form
                ref="mailingAddress"
                :editing="isBaseAddressEditMode"
                :schema="baseAddressSchema"
                :address="baseAddress"
                @update:address="updateAddress"
                @valid="checkBaseAddressValidity"
              />
            </div>
          </template>
        </div>

        <div v-if="editEnabled">
          <v-divider class="mt-3 mb-10"></v-divider>
          <div class="form__btns">
            <v-btn
              large
              class="save-btn"
              v-bind:class="{ disabled: btnLabel == 'Saved' }"
              :color="btnLabel == 'Saved' ? 'success' : 'primary'"
              :disabled="!isSaveEnabled()"
              :loading="btnLabel == 'Saving'"
              aria-label="Save Account Information"
              @click="updateDetails()"
            >
              <v-expand-x-transition>
                <v-icon v-show="btnLabel == 'Saved'">mdi-check</v-icon>
              </v-expand-x-transition>
              <span class="save-btn__label">{{ btnLabel }}</span>
            </v-btn>
            <v-btn
              large
              depressed
              class="ml-2"
              color="default"
              aria-label="Reset Account Information"
              @click="resetForm"
              data-test="reset-button"
            >Reset</v-btn>
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
    data-test='modal-suspend-account'
    >
      <template v-slot:icon>
        <v-icon large color="error">mdi-alert-circle-outline</v-icon>
      </template>
      <template v-slot:text>
        <p class="px-10">{{ dialogText }}<br/></p>
        <v-form ref="suspensionReasonForm" id="suspensionReasonForm">
          <v-select
            class="px-10"
            filled
            label="Reason for Suspension"
            req
            :rules="suspensionSelectRules"
            :items="suspensionReasonCodes"
            item-text="desc"
            item-value="code"
            v-model="selectedSuspensionReasonCode"
            v-if="isAccountStatusActive"
            data-test='select-suspend-account-reason'
          />
        </v-form>
      </template>
      <template v-slot:actions>
        <v-btn
          large
          class="font-weight-bold white--text btn-dialog"
          :color="getDialogStatusButtonColor(currentOrganization.orgStatus)"
          data-test='btn-suspend-dialog'
          @click="confirmSuspendAccount()"
        >
          {{ isAccountStatusActive ? 'Suspend' : 'Unsuspend' }}
        </v-btn>
        <v-btn
          large
          depressed
          class="btn-dialog"
          @click="closeSuspendAccountDialog()"
          data-test='btn-cancel-suspend-dialog'
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
    data-test='modal-suspension-complete'
    >
      <template v-slot:icon>
        <v-icon large color="primary">mdi-check</v-icon>
      </template>
      <template v-slot:actions>
        <v-btn
          large
          depressed
          class="font-weight-bold white--text btn-dialog"
          @click="closeSuspensionCompleteDialog()"
          data-test='btn-suspend-confirm-dialog'
          color="primary"
        >
          OK
        </v-btn>
      </template>
    </ModalDialog>
  </v-container>
</template>

<script lang="ts">
import { AccessType, Account, AccountStatus, LDFlags, Pages, Permission, Role, SessionStorageKeys } from '@/util/constants'
import { Component, Mixins } from 'vue-property-decorator'
import { CreateRequestBody, Member, Organization } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import { AccountSettings } from '@/models/account-settings'
import { Address } from '@/models/address'
import BaseAddressForm from '@/components/auth/common/BaseAddressForm.vue'
import { Code } from '@/models/Code'
import ConfigHelper from '@/util/config-helper'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import LinkedBCOLBanner from '@/components/auth/common/LinkedBCOLBanner.vue'
import ModalDialog from '../../common/ModalDialog.vue'
import OrgAdminContact from '@/components/auth/account-settings/account-info/OrgAdminContact.vue'
import OrgModule from '@/store/modules/org'
import { addressSchema } from '@/schemas'
import { getModule } from 'vuex-module-decorators'
import { namespace } from 'vuex-class'

const CodesModule = namespace('codes')

@Component({
  components: {
    BaseAddressForm,
    OrgAdminContact,
    LinkedBCOLBanner,
    ModalDialog
  },
  computed: {
    ...mapState('user', [
      'currentUser'
    ]),
    ...mapState('org', [
      'currentOrganization',
      'currentMembership',
      'currentOrgAddress',
      'permissions'
    ])
  },
  methods: {
    ...mapActions('org', ['updateOrg', 'syncAddress', 'syncOrganization', 'suspendOrganization']),
    ...mapMutations('org', ['setCurrentOrganizationAddress'])
  }
})
export default class AccountInfo extends Mixins(AccountChangeMixin) {
  @CodesModule.State('suspensionReasonCodes') private suspensionReasonCodes!: Code[]

  private orgStore = getModule(OrgModule, this.$store)
  private btnLabel = 'Save'
  private readonly currentOrganization!: Organization
  private readonly currentOrgAddress!: Address
  private readonly currentMembership!: Member
  private readonly currentUser!: KCUserProfile
  private readonly permissions!: string[]
  private dialogTitle: string = ''
  private dialogText: string = ''
  private selectedSuspensionReasonCode: string = ''
  private suspensionCompleteDialogText: string = ''
  private isSuspensionReasonFormValid: boolean = false

  private readonly updateOrg!: (
    requestBody: CreateRequestBody
  ) => Promise<Organization>
  private readonly syncAddress!: () => Address
  protected readonly syncOrganization!: (currentAccount: number) => Promise<Organization>
  protected readonly suspendOrganization!: (selectedSuspensionReasonCode: string) => Promise<Organization>
  private orgName = ''
  private errorMessage: string = ''
  private readonly setCurrentOrganizationAddress!: (address: Address) => void
  private isBaseAddressValid: boolean = false
  private isCompleteAccountInfo = true

  private baseAddressSchema: {} = addressSchema

  $refs: {
    editAccountForm: HTMLFormElement,
    mailingAddress:HTMLFormElement,
    suspendAccountDialog:ModalDialog,
    suspensionCompleteDialog:ModalDialog,
    suspensionReasonForm: HTMLFormElement
  }

  private isFormValid (): boolean {
    return !!this.orgName || this.orgName === this.currentOrganization?.name
  }

  private get isStaff (): boolean {
    return this.currentUser.roles.includes(Role.Staff)
  }

  private get isSuspendButtonVisible (): boolean {
    return (this.currentOrganization.statusCode === AccountStatus.ACTIVE || this.currentOrganization.statusCode === AccountStatus.SUSPENDED) && this.currentUser.roles.includes(Role.StaffSuspendAccounts)
  }

  get editAccountUrl () {
    return Pages.EDIT_ACCOUNT_TYPE
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

  private keyDown (address: Address) {
    this.enableBtn()
  }

  private get baseAddress () {
    return this.currentOrgAddress
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
    this.setCurrentOrganizationAddress(address)
    this.enableBtn()
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

  private async setup () {
    const accountSettings = this.getAccountFromSession()
    this.orgName = this.currentOrganization?.name || ''
    if (this.isPremiumAccount || this.enablePaymentMethodSelectorStep) {
      await this.syncAddress()
      // show this part only when enablePaymentMethodSelectorStep= true and account is not anon
      if (!this.anonAccount && this.enableMandatoryAddress) {
        if (Object.keys(this.currentOrgAddress).length === 0) {
          this.isCompleteAccountInfo = false
          this.errorMessage = this.isAddressEditable ? 'Your account info is incomplete. Please enter your address in order to proceed.'
            : 'This accounts profile is incomplete. You will not be able to proceed until an account administrator entered the missing information for this account.'
          this.$refs.editAccountForm?.validate() // validate form fields and show error message
          this.$refs.mailingAddress?.$refs.baseAddress?.$refs.addressForm?.validate() // validate form fields and show error message for address component from sbc-common-comp
        }
      }
    } else {
      // inorder to hide the address if not premium account
      this.baseAddress = null
    }
  }

  protected getAccountFromSession (): AccountSettings {
    return JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccount || '{}'))
  }

  private async resetForm () {
    this.setup()
    await this.syncAddress()
  }

  get isPremiumAccount (): boolean {
    return this.currentOrganization?.orgType === Account.PREMIUM
  }

  get anonAccount (): boolean {
    return this.currentOrganization?.accessType === AccessType.ANONYMOUS
  }

  // todo fix it completely by using permissions
  private canChangeAccountName (): boolean {
    if (this.currentOrganization?.accessType === AccessType.ANONYMOUS) {
      return false
    }
    // Premium account name cant be updated
    if (this.isPremiumAccount) {
      return false
    }
    return [Permission.CHANGE_ORG_NAME].some(per => this.permissions.includes(per))
  }

  private isSaveEnabled () {
    if (this.isPremiumAccount || this.enablePaymentMethodSelectorStep) {
      // org name is read only ;the only thing which they can change is address
      // detect any change in address
      return this.isBaseAddressValid
    }
    if (this.currentOrganization?.orgType === Account.BASIC) {
      return this.isFormValid()
    }
    // nothing can be changed in anonymous org
    return false
  }

  private get enablePaymentMethodSelectorStep (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.PaymentTypeAccountCreation) || false
  }

  private get enableMandatoryAddress (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.EnableMandatoryAddress) || false
  }

  private get enableUpgradeDowngrade (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.EnableUpgradeDowngrade) || false
  }

  private enableBtn () {
    this.btnLabel = 'Save'
  }

  private async updateDetails () {
    this.errorMessage = ''
    this.btnLabel = 'Saving'
    let createRequestBody: CreateRequestBody = {
      name: this.orgName
    }
    if (this.baseAddress) {
      createRequestBody.mailingAddress = { ...this.baseAddress }
    }
    try {
      await this.updateOrg(createRequestBody)
      this.$store.commit('updateHeader')
      this.btnLabel = 'Saved'
      // assume info is complete
      if (this.baseAddress) {
        this.isCompleteAccountInfo = true
      }
    } catch (err) {
      this.btnLabel = 'Save'
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
            'An error occurred while attempting to create your account.'
      }
    }
  }

  private readonly accountNameRules = [
    v => !!v || 'An account name is required'
  ]

  private checkBaseAddressValidity (isValid) {
    this.isBaseAddressValid = !!isValid
  }

  get editEnabled () : boolean {
    return [Permission.CHANGE_ADDRESS, Permission.CHANGE_ORG_NAME].some(per => this.permissions.includes(per))
  }

  get isAddressEditable () : boolean {
    return [Permission.CHANGE_ADDRESS].some(per => this.permissions.includes(per))
  }

  get isAddressViewable () : boolean {
    return [Permission.VIEW_ADDRESS].some(per => this.permissions.includes(per))
  }

  get isAdminContactViewable () : boolean {
    return [Permission.VIEW_ADMIN_CONTACT].some(per => this.permissions.includes(per))
  }

  get isBaseAddressEditMode () : boolean {
    if (this.isAddressEditable) {
      return true
    } else if (this.isAddressViewable) {
      return false
    }
    return false
  }

  get isAccountStatusActive () : boolean {
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

  .name, .value {
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
    display: inline-block
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

.save-btn.disabled {
  pointer-events: none;
}

.save-btn__label {
  padding-left: 0.2rem;
  padding-right: 0.2rem;
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
</style>
