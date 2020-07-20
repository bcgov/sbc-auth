<template>
  <v-container class="pa-0">
    <div>
      <v-form ref="editAccountForm">
        <v-alert type="error" class="mb-6" v-show="errorMessage">
          {{ errorMessage }}
        </v-alert>

        <ul class="nv-list" v-can:VIEW_ACCOUNT.hide>
          <li class="nv-list-item mb-10">
            <div class="name" id="accountName">Account Name</div>
            <div class="value" aria-labelledby="accountName">
              <div class="value__title">{{ currentOrganization.name }}</div>
            </div>
          </li>
          <li class="nv-list-item mb-10">
            <div class="name" id="accountStatus">Status</div>
            <div class="value" aria-labelledby="accountStatus">
              <div class="value__title">{{ currentOrganization.orgStatus }}</div>
            </div>
          </li>
        </ul>

        <ul class="nv-list" v-show="!anonAccount">
          <li class="nv-list-item mb-10">
            <div class="name" id="accountType">Account Type</div>
            <div class="value" aria-labelledby="accountType">
              <div class="value__title">{{ isPremiumAccount ? 'Premium' : 'Basic' }}</div>
              <div v-can:CHANGE_ACCOUNT_TYPE.hide>
                <router-link :to="editAccountUrl" v-can:CHANGE_ACCOUNT_TYPE.hide >Change account type</router-link>
              </div>
            </div>
          </li>
          <li class="nv-list-item mb-12" v-if="isPremiumAccount">
            <div class="name mb-3" id="accountName">Linked BC Online Account Details</div>
            <v-alert dark color="primary" class="bcol-acc px-7 py-5">
              <div class="bcol-acc__name">
                {{ currentOrganization.name }}
              </div>
              <ul class="bcol-acc__meta" v-if="isPremiumAccount && currentOrgPaymentSettings">
                <li>
                  BC Online Account No: {{currentOrgPaymentSettings.bcolAccountId}}
                </li>
                <li>
                  Prime Contact ID: {{currentOrgPaymentSettings.bcolUserId}}
                </li>
              </ul>
            </v-alert>
          </li>
        </ul>
        <ul class="nv-list">
          <li class="nv-list-item mb-12">
            <div class="name" id="adminContact">Admin Contact</div>
            <div class="value" aria-labelledby="adminContact">
              <OrgAdminContact></OrgAdminContact>
            </div>
          </li>
        </ul>

        <fieldset v-if="!isPremiumAccount" v-can:CHANGE_ORG_NAME.hide>
          <legend class="mb-4">Account Details</legend>
          <v-text-field
            filled
            clearable
            required
            label="Account Name"
            :rules="accountNameRules"
            v-can:CHANGE_ORG_NAME.disable
            :disabled="!canChangeAccountName()"
            v-if="!isPremiumAccount"
            v-model="orgName"
            v-on:keydown="enableBtn()"
          >
          </v-text-field>
        </fieldset>

        <template v-if="isPremiumAccount && currentOrgAddress">
          <h4 class="mb-4">Mailing Address</h4>
          <BaseAddress v-can:CHANGE_ADDRESS.hide
                  :inputAddress="currentOrgAddress"
                  @key-down="keyDown()"
                  @address-update="updateAddress"
                  @is-form-valid="checkBaseAddressValidity"
                  :key="addressKey"
          >
          </BaseAddress>
          <div class="value value__title" aria-labelledby="mailingAddress" v-if="currentOrgAddress" v-can:VIEW_ADDRESS.hide>
            <div>{{ currentOrgAddress.street }}</div>
            <div v-if="currentOrgAddress.streetAdditional">{{ currentOrgAddress.streetAdditional }}</div>
            <div>{{ currentOrgAddress.city }}, {{ currentOrgAddress.region }}  {{ currentOrgAddress.postalCode }}</div>
            <div>{{ currentOrgAddress.country}}</div>
          </div>
        </template>

        <v-divider class="mt-3 mb-10" v-if="editEnabled"></v-divider>

        <div class="form__btns" v-if="editEnabled">
          <v-btn
            large
            class="save-btn"
            v-bind:class="{ disabled: btnLabel == 'Saved' }"
            :color="btnLabel == 'Saved' ? 'success' : 'primary'"
            :disabled="!isSaveEnabled()"
            :loading="btnLabel == 'Saving'"
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
            @click="resetForm"
            data-test="reset-button"
          >Reset</v-btn>
        </div>
      </v-form>
    </div>
  </v-container>
</template>

<script lang="ts">
import { AccessType, Account, Pages, Permission, SessionStorageKeys } from '@/util/constants'
import { Component, Mixins, Vue, Watch } from 'vue-property-decorator'
import {
  CreateRequestBody,
  Member,
  MembershipType,
  Organization
} from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import { AccountSettings } from '@/models/account-settings'
import { Address } from '@/models/address'
import BaseAddress from '@/components/auth/BaseAddress.vue'
import ConfigHelper from '@/util/config-helper'
import OrgAdminContact from '@/components/auth/OrgAdminContact.vue'
import OrgModule from '@/store/modules/org'
import { PaymentSettings } from '@/models/PaymentSettings'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    BaseAddress,
    OrgAdminContact
  },
  computed: {
    ...mapState('org', [
      'currentOrganization',
      'currentMembership',
      'currentOrgAddress',
      'currentOrgPaymentSettings',
      'permissions'
    ])
  },
  methods: {
    ...mapActions('org', ['updateOrg', 'syncAddress', 'syncOrganization', 'syncPaymentSettings']),
    ...mapMutations('org', ['setCurrentOrganizationAddress'])
  }
})
export default class AccountInfoEdit extends Mixins(AccountChangeMixin) {
  private orgStore = getModule(OrgModule, this.$store)
  private btnLabel = 'Save'
  private readonly currentOrganization!: Organization
  private readonly currentOrgAddress!: Address
  private readonly currentOrgPaymentSettings!: PaymentSettings
  private readonly currentMembership!: Member
  private readonly permissions!: string[]

  private readonly updateOrg!: (
    requestBody: CreateRequestBody
  ) => Promise<Organization>
  private readonly syncAddress!: () => Address
  protected readonly syncOrganization!: (currentAccount: number) => Promise<Organization>
  protected readonly syncPaymentSettings!: (currentAccount: number) => Promise<PaymentSettings>
  private orgName = ''
  private errorMessage: string = ''
  private readonly setCurrentOrganizationAddress!: (address: Address) => void
  private isBaseAddressValid: boolean = false

  private isFormValid (): boolean {
    return !!this.orgName || this.orgName === this.currentOrganization?.name
  }

  get addressKey () {
    return JSON.stringify(this.currentOrgAddress)
  }

  get editAccountUrl () {
    return Pages.EDIT_ACCOUNT_TYPE
  }

  private async mounted () {
    const accountSettings = this.getAccountFromSession()
    await this.syncOrganization(accountSettings.id)
    this.setAccountChangedHandler(this.setup)
    this.setup()
  }

  private keyDown (address: Address) {
    this.enableBtn()
  }

  private updateAddress (address: Address) {
    this.setCurrentOrganizationAddress(address)
    this.enableBtn()
  }

  private async setup () {
    const accountSettings = this.getAccountFromSession()
    this.orgName = this.currentOrganization?.name || ''
    if (this.isPremiumAccount) {
      await this.syncPaymentSettings(accountSettings.id)
      await this.syncAddress()
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

  private canChangeAccountName (): boolean {
    if (this.currentOrganization?.accessType === AccessType.ANONYMOUS) {
      return false
    }
    // Premium account name cant be updated
    if (this.isPremiumAccount) {
      return false
    }
    return true
  }

  private isSaveEnabled () {
    if (this.currentOrganization?.orgType === Account.BASIC) {
      return this.isFormValid()
    }
    if (this.isPremiumAccount) {
      // org name is read only ;the only thing which they can change is address
      // detect any change in address
      return this.isBaseAddressValid
    }
    // nothing can be changed in anonymous org
    return false
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
    if (this.isPremiumAccount) {
      createRequestBody.mailingAddress = this.currentOrgAddress
    }
    try {
      await this.updateOrg(createRequestBody)
      this.$store.commit('updateHeader')
      this.btnLabel = 'Saved'
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
  vertical-align: top;

  .name, .value {
    display: inline-block;
    vertical-align: top;
  }

  .name {
    min-width: 10rem;
    font-weight: 700;
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
</style>
