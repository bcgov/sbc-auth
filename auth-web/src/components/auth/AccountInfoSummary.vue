<template>
  <v-container class="pa-0">
    <v-form ref="viewAccountForm">
      <ul class="nv-list">
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
        <li class="nv-list-item mb-10">
          <div class="name" id="accountType">Account Type</div>
          <div class="value" aria-labelledby="accountType">
            <div class="value__title">{{ isPremiumAccount ? 'Premium' : 'Basic' }}</div>
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
        <li class="nv-list-item mb-10">
          <div class="name" id="adminContact">Admin Contact</div>
          <div class="value" aria-labelledby="adminContact">
            <OrgAdminContact></OrgAdminContact>
          </div>
        </li>

        <li class="nv-list-item mb-10" v-if="currentOrgAddress">
          <div class="name" id="mailingAddress">Mailing Address</div>
          <div class="value value__title" aria-labelledby="mailingAddress">
            <div>{{ currentOrgAddress.street }}</div>
            <div v-if="currentOrgAddress.streetAdditional">{{ currentOrgAddress.streetAdditional }}</div>
            <div>{{ currentOrgAddress.city }}, {{ currentOrgAddress.region }}  {{ currentOrgAddress.postalCode }}</div>
            <div>{{ currentOrgAddress.country}}</div>
          </div>
        </li>
      </ul>

    </v-form>
  </v-container>
</template>

<script lang="ts">
import { AccessType, Account, Pages, SessionStorageKeys } from '@/util/constants'
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
      'currentOrgPaymentSettings'
    ])
  },
  methods: {
    ...mapActions('org', ['updateOrg', 'syncAddress', 'syncOrganization', 'syncPaymentSettings']),
    ...mapMutations('org', ['setCurrentOrganizationAddress'])
  }
})
export default class AccountInfoSummary extends Mixins(AccountChangeMixin) {
  private orgStore = getModule(OrgModule, this.$store)

  private readonly currentOrganization!: Organization
  private readonly currentOrgAddress!: Address
  private readonly currentOrgPaymentSettings!: PaymentSettings
  private readonly currentMembership!: Member

  private async mounted () {
    const accountSettings = this.getAccountFromSession()
  }

  protected getAccountFromSession (): AccountSettings {
    return JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccount || '{}'))
  }

  get isPremiumAccount (): boolean {
    return this.currentOrganization?.orgType === Account.PREMIUM
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
