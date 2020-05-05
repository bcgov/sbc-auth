<template>
  <v-container class="pa-0">
    <header class="view-header mb-10">
      <h2 class="view-header__title">Account Information</h2>
    </header>
    <v-form ref="editAccountForm">
      <v-alert type="error" class="mb-6" v-show="errorMessage">
        {{ errorMessage }}
      </v-alert>

      <ul class="nv-list">
        <li class="nv-list-item mb-9">
          <div class="name" id="accountType">Account Type</div>
          <div class="value" aria-labelledby="accountType">
            <div class="value__title">{{ isPremiumAccount ? 'PREMIUM' : 'BASIC' }}</div>
            <ul class="bcol-acc__meta mt-1" v-if="isPremiumAccount">
              <li>
                BC Online Account No: 18670
              </li>
              <li>
                Authorizing User ID: PB25020
              </li>
            </ul>
            <!--
            <div class="mt-2">
              <a class="change-account-link" href="">Change Account</a>
            </div>
            -->
          </div>
        </li>
        <li class="nv-list-item mb-12" v-if="isPremiumAccount">
          <div class="name" id="accountName">Account Name</div>
          <div class="value" aria-labelledby="accountType">
            <div class="value__title">{{ orgName }}</div>
            <div class="mt-1">Premium accounts use your existing BC Online account name and cannot be modified.</div>
          </div>
        </li>
      </ul>

      <fieldset v-if="!isPremiumAccount">
        <legend class="mb-4">Account Details</legend>
        <v-text-field
          filled
          clearable
          required
          label="Account Name"
          :rules="accountNameRules"
          v-if="!isPremiumAccount"
          v-model="orgName"
          v-on:keydown="enableBtn()"
        >
        </v-text-field>
      </fieldset>

      <BaseAddress
        :inputAddress="currentOrgAddress"
        @key-down="keyDown()"
        @address-update="updateAddress"
        v-if="isPremiumAccount && currentOrgAddress"
        :disabled="!canChangeAddress()"
      >
      </BaseAddress>
      <div class="form__btns">
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
      </div>
    </v-form>
  </v-container>
</template>

<script lang="ts">
import { Component, Mixins, Vue, Watch } from 'vue-property-decorator'
import {
  CreateRequestBody,
  Member,
  MembershipType,
  Organization
} from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import { Account } from '@/util/constants'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import { Address } from '@/models/address'
import BaseAddress from '@/components/auth/BaseAddress.vue'
import OrgModule from '@/store/modules/org'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    BaseAddress
  },
  computed: {
    ...mapState('org', [
      'currentOrganization',
      'currentMembership',
      'currentOrgAddress'
    ])
  },
  methods: {
    ...mapActions('org', ['updateOrg', 'syncAddress', 'syncOrganization']),
    ...mapMutations('org', ['setCurrentOrganizationAddress'])
  }
})
export default class AccountInfo extends Mixins(AccountChangeMixin) {
  private orgStore = getModule(OrgModule, this.$store)
  private btnLabel = 'Save'
  private readonly currentOrganization!: Organization
  private readonly currentOrgAddress!: Address
  private readonly currentMembership!: Member
  private readonly updateOrg!: (
    requestBody: CreateRequestBody
  ) => Promise<Organization>
  private readonly syncAddress!: () => Address
  private readonly syncOrganization!: () => Organization
  private orgName = ''
  private errorMessage: string = ''
  private readonly setCurrentOrganizationAddress!: (address: Address) => void
  private addressTocuhed = false

  private isFormValid (): boolean {
    return !!this.orgName || this.orgName === this.currentOrganization?.name
  }

  private async mounted () {
    this.setAccountChangedHandler(this.syncOrgName)
    this.syncOrgName()
    if (this.isPremiumAccount) {
      await this.syncAddress()
    }
  }

  private keyDown (address: Address) {
    this.addressTocuhed = true
    this.enableBtn()
  }

  private updateAddress (address: Address) {
    this.setCurrentOrganizationAddress(address)
    this.addressTocuhed = true
    this.enableBtn()
  }

  private syncOrgName () {
    this.orgName = this.currentOrganization?.name || ''
  }

  private canChangeAddress (): boolean {
    if (this.isPremiumAccount) {
      const premiumOwner =
        this.currentMembership?.membershipTypeCode === MembershipType.Owner || this.currentMembership?.membershipTypeCode === MembershipType.Admin
      return premiumOwner
    }
    return false
  }

  get isPremiumAccount (): boolean {
    return this.currentOrganization?.orgType === Account.PREMIUM
  }

  private canChangeAccountName (): boolean {
    if (this.currentOrganization?.accessType === Account.ANONYMOUS) {
      return false
    }
    // Premium account name cant be updated
    if (this.isPremiumAccount) {
      return false
    }
    switch (this.currentMembership?.membershipTypeCode) {
      case MembershipType.Owner:
        return true
      default:
        return false
    }
  }

  private isSaveEnabled () {
    if (this.currentOrganization?.orgType === Account.BASIC) {
      return this.isFormValid() && this.canChangeAccountName()
    }
    if (this.isPremiumAccount) {
      // org name is read only ;the only thing which they can change is address
      // detect any change in address
      return this.addressTocuhed
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
