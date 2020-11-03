import { AccessType } from '@/util/constants'
<template>
  <div>
    <p class="mb-7" v-if="!isAccountChange">There is no cost to create a BC Registries account. You only pay for the services and products you purchase.</p>
    <p class="mb-7" v-if="isAccountChange">There is no cost to change a BC Registries account type. You only pay for the services and products you purchase.</p>
    <v-row>
      <v-col
        class="d-flex align-stretch"
        sm="12" md="6"
      >
        <v-card
          class="account-card pa-10 pt-9 elevation-2"
          :class="{'active': selectedAccountType == ACCOUNT_TYPE.BASIC}"
          flat
          outlined
          hover
          @click="selectAccountType(ACCOUNT_TYPE.BASIC)"
        >
          <div class="account-type">
            <div class="account-type__name mt-n1 mb-2">
              Basic
            </div>
            <div class="account-type__title mb-8">
              I make 10 transactions per month or less
            </div>
            <ul class="account-type__details ml-1">
              <li class="mb-4">For users who file on behalf of their own businesses or conduct a limited number of searches</li>
              <li class="mb-4">Credit card payment only</li>
              <li>Up to 10 purchases per month</li>
            </ul>
          </div>

          <!-- State Button (Create Account) -->
          <div class="mt-9" v-if="!isAccountChange">
            <v-btn large block depressed color="primary" class="font-weight-bold"
              :outlined="selectedAccountType != ACCOUNT_TYPE.BASIC"
              @click="selectAccountType(ACCOUNT_TYPE.BASIC)">
              {{ selectedAccountType == ACCOUNT_TYPE.BASIC ? 'SELECTED' : 'SELECT'}}
            </v-btn>
          </div>

          <!-- State Button (Change Account) -->
          <div class="mt-9" v-if="isAccountChange">
            <v-btn large block depressed color="primary" class="font-weight-bold"
              :outlined="selectedAccountType != ACCOUNT_TYPE.BASIC"
              @click="selectAccountType(ACCOUNT_TYPE.BASIC)">
              <span v-if="accountTypeBeforeChange == ACCOUNT_TYPE.BASIC">CURRENT ACCOUNT</span>
              <span v-if="accountTypeBeforeChange != ACCOUNT_TYPE.BASIC">{{ selectedAccountType == ACCOUNT_TYPE.BASIC ? 'SELECTED' : 'SELECT'}}</span>
            </v-btn>
          </div>

        </v-card>
      </v-col>
      <v-col
        class="d-flex align-stretch"
        sm="12" md="6"
      >
        <v-card
          class="account-card pa-10 pt-9 elevation-2 d-flex"
          :class="{'active': selectedAccountType == ACCOUNT_TYPE.PREMIUM}"
          flat
          outlined
          hover
          @click="selectAccountType(ACCOUNT_TYPE.PREMIUM)"
        >
          <div class="account-type">
            <div class="account-type__name mt-n1 mb-2">PREMIUM</div>
            <div class="account-type__title mb-8">I make more than 10 transactions per month</div>
            <ul class="account-type__details ml-1 mb-6">
              <li class="mb-4">For firms and companies who search frequently or file for a large number of businesses</li>
              <li class="mb-4">Uses your BC Online account to pay for products and services</li>
              <li class="mb-4">Unlimited transactions</li>
              <li>Requires an existing BC Online account and Prime Contact credentials to complete.</li>
            </ul>
            <div>
              <v-btn text color="primary" class="bcol-link px-2" href="https://www.bconline.gov.bc.ca/" target="_blank" rel="noopener noreferrer">
                <v-icon>mdi-help-circle-outline</v-icon>
                <span>How do I get a BC Online Account?</span>
              </v-btn>
            </div>

            <!-- State Button (Create Account) -->
            <div class="mt-9" v-if="!isAccountChange">
              <v-btn large block depressed color="primary" class="font-weight-bold"
                :outlined="selectedAccountType != ACCOUNT_TYPE.PREMIUM"
                @click="selectAccountType(ACCOUNT_TYPE.PREMIUM)">
                {{ selectedAccountType == ACCOUNT_TYPE.PREMIUM ? 'SELECTED' : 'SELECT' }}
              </v-btn>
            </div>

            <!-- State Button (Change Account) -->
            <div class="mt-9" v-if="isAccountChange">
              <v-btn large block depressed color="primary" class="font-weight-bold"
                :outlined="selectedAccountType != ACCOUNT_TYPE.PREMIUM"
                @click="selectAccountType(ACCOUNT_TYPE.PREMIUM)">
                <span v-if="accountTypeBeforeChange == ACCOUNT_TYPE.PREMIUM">CURRENT ACCOUNT</span>
                <span v-if="accountTypeBeforeChange != ACCOUNT_TYPE.PREMIUM">{{ selectedAccountType == ACCOUNT_TYPE.PREMIUM ? 'SELECTED' : 'SELECT'}}</span>
              </v-btn>
            </div>

          </div>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col
        cols="12"
        class="form__btns mt-6 pb-0 text-right"
      >
        <v-btn large color="primary" class="mr-3" @click="goNext" :disabled='!canContinue'>
          <span>Next</span>
          <v-icon class="ml-2">mdi-arrow-right</v-icon>
        </v-btn>
        <ConfirmCancelButton
          :showConfirmPopup="false"
          :clear-current-org="!isAccountChange"
          :target-route="cancelUrl"
        ></ConfirmCancelButton>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">

import { AccessType, Account, LoginSource, SessionStorageKeys } from '@/util/constants'
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { mapMutations, mapState } from 'vuex'
import ConfigHelper from '@/util/config-helper'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import { Organization } from '@/models/Organization'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'

  @Component({
    components: {
      ConfirmCancelButton
    },
    computed: {
      ...mapState('org', [
        'currentOrganization',
        'accountTypeBeforeChange',
        'currentOrganizationType'
      ]),
      ...mapState('user', ['currentUser'])
    },
    methods: {
      ...mapMutations('org', [
        'setSelectedAccountType',
        'setCurrentOrganization',
        'setCurrentOrganizationType',
        'resetCurrentOrganisation',
        'setAccountTypeBeforeChange',
        'setAccessType'
      ])
    }
  })
export default class AccountTypeSelector extends Mixins(Steppable) {
  private readonly ACCOUNT_TYPE = Account
  private selectedAccountType = ''
  private readonly setSelectedAccountType!: (selectedAccountType: Account) => void
  private readonly setAccountTypeBeforeChange!: (accountTypeBeforeChange: string) => void
  private readonly setCurrentOrganization!: (organization: Organization) => void
  private readonly setCurrentOrganizationType!: (orgType: string) => void
  private readonly setAccessType!: (accessType: string) => void
  private readonly currentOrganization!: Organization
  private readonly accountTypeBeforeChange!: string
  private readonly currentOrganizationType!: string
  private readonly resetCurrentOrganisation!: () => void
  protected readonly currentUser!: KCUserProfile
  @Prop() isAccountChange: boolean
  @Prop() cancelUrl: string

  private async mounted () {
    if (this.isAccountChange) {
      // Account change needs all the org details as such..so do not clear any details...
      // Account change doesnt create a new org
      if (!this.accountTypeBeforeChange) { // do not reset the originalAccountType after first time..
        this.setAccountTypeBeforeChange(this.currentOrganization.orgType)
      }
      this.selectedAccountType = this.currentOrganization.orgType
      this.setCurrentOrganizationType(this.selectedAccountType)
    } else {
      // first time to the page , start afresh..this is Create New account flow
      if (!this.currentOrganization) {
        this.setCurrentOrganization({ name: '' })
      }
      this.selectedAccountType = (this.currentOrganizationType === this.ACCOUNT_TYPE.UNLINKED_PREMIUM)
        ? this.ACCOUNT_TYPE.PREMIUM : this.currentOrganizationType
      this.setAccessType(this.getOrgAccessType())
    }
  }

  private selectAccountType (accountType) {
    // to reset any existing details ;user might have went to user profile ;came back and selects another type scenarios
    if (!this.isAccountChange) {
      this.resetCurrentOrganisation()
    }
    this.setSelectedAccountType(accountType)
    this.setCurrentOrganizationType(accountType)
    this.selectedAccountType = accountType
  }

  private getOrgAccessType () {
    let isBceidUser = this.currentUser?.loginSource === LoginSource.BCEID
    let isExtraProvice = JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.ExtraProvincialUser || '{}'))
    return isBceidUser ? (isExtraProvice ? AccessType.EXTRA_PROVINCIAL : AccessType.REGULAR_BCEID) : AccessType.REGULAR
  }

  private goNext () {
    this.stepForward(this.selectedAccountType === this.ACCOUNT_TYPE.PREMIUM)
  }

  private get canContinue () {
    if (this.isAccountChange) {
      return this.accountTypeBeforeChange !== this.selectedAccountType
    } else {
      return this.selectedAccountType
    }
  }

  private cancel () {
    this.$router.push({ path: '/home' })
  }
}
</script>

<style lang="scss" scoped>
@import "$assets/scss/theme.scss";

.col {
  padding: 1rem !important;
}

.account-card {
  display: flex;
  flex-direction: column;
  position: relative;
  background-color: var(--v-grey-lighten4) !important;

  &:hover {
    border-color: var(--v-primary-base) !important;
  }

  &.active {
    box-shadow: 0 0 0 2px inset var(--v-primary-base), 0 3px 1px -2px rgba(0,0,0,.2),0 2px 2px 0 rgba(0,0,0,.14),0 1px 5px 0 rgba(0,0,0,.12) !important;
  }
}

.theme--light.v-card.v-card--outlined.active {
  border-color: var(--v-primary-base);
}

.account-type {
  flex: 1 1 auto;
}

.account-type__title {
  line-height: 1.75rem;
  font-size: 1.5rem;
  font-weight: 700;
}

.account-type__name {
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.9375rem;
  color: var(--v-grey-darken1);
}

.v-btn.bcol-link {
  text-align: left;

  .v-icon {
    margin-top: 0.1rem;
    margin-right: 0.5rem;
  }

  span {
    text-decoration: underline;
  }
}

ul {
  list-style: none; /* Remove default bullets */
  font-size: 0.875rem;
}

ul li::before {
  content: "\2022";  /* Add content: \2022 is the CSS Code/unicode for a bullet */
  color: var(--v-primary-base);
  font-weight: 700;
  display: inline-block;
  width: 1.5rem;
  margin-left: -1.5rem;
}

.selected-icon {
  opacity: 0;
  position: absolute;
  top: 1.75rem;
  right: 2.5rem;
  transform: scale(0.25);
  transform-origin: 50% 50%;
  transition: all ease-out 0.5s;

  .v-icon {
    color: #ffffff;
  }
}

.active .selected-icon {
  opacity: 1;
  transform: scale(1);
}

.select-account-btn  {
  width: 20rem;
  font-weight: 700;
}
</style>
