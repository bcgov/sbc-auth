<template>
  <div data-test="div-stepper-container">
    <p class="mb-7">
      There is no cost to create a BC Registries account. You only pay for the services and products you purchase.
    </p>
    <v-row v-display-mode>
      <v-col
        class="d-flex align-stretch"
        sm="12"
        md="6"
      >
        <v-card
          class="account-card pa-8 elevation-2"
          :class="{'active': selectedAccountType == ACCOUNT_TYPE.BASIC}"
          flat
          outlined
          hover
          data-test="div-stepper-basic"
          :disabled="isCurrentSelectedProductsPremiumOnly"
          @click="selectAccountType(ACCOUNT_TYPE.BASIC)"
        >
          <div class="account-type">
            <div class="account-type__title">
              Basic
            </div>
            <div class="account-type__name">
              Pay-as-you-go
            </div>
            <div class="account-type__summary">
              For people who file on behalf of their own businesses or conduct limited searches.
            </div>
            <ul class="account-type__details">
              <li>10 transactions per month</li>
              <li>5 team members per account</li>
              <li>Pay by credit card and online banking</li>
            </ul>
          </div>

          <!-- State Button (Create Account) -->
          <div class="mt-10">
            <v-btn
              large
              block
              depressed
              color="primary"
              class="font-weight-bold"
              data-test="btn-stepper-basic-select"
              :outlined="selectedAccountType != ACCOUNT_TYPE.BASIC"
              @click="selectAccountType(ACCOUNT_TYPE.BASIC)"
            >
              {{ selectedAccountType == ACCOUNT_TYPE.BASIC ? 'SELECTED' : 'SELECT' }}
            </v-btn>
          </div>
        </v-card>
      </v-col>
      <v-col
        class="d-flex align-stretch"
        sm="12"
        md="6"
      >
        <v-badge color>
          <span
            v-if="isCurrentSelectedProductsPremiumOnly"
            slot="badge"
            data-test="badge-account-premium"
          >
            <v-chip
              class="premium-badge-chip"
              label
            >
              <span>A Premium Account type is required based on the services you have selected.</span>
            </v-chip>
          </span>
          <v-card
            class="account-card pa-8 elevation-2"
            :class="{'active': selectedAccountType == ACCOUNT_TYPE.PREMIUM}"
            flat
            outlined
            hover
            data-test="div-stepper-premium"
            @click="selectAccountType(ACCOUNT_TYPE.PREMIUM)"
          >
            <div class="account-type">
              <div class="account-type__title">
                Premium
              </div>
              <div class="account-type__name">
                Pre-authorized
              </div>
              <div class="account-type__summary">
                For firms and companies who search frequently or file for a large number of businesses.
              </div>
              <ul class="account-type__details">
                <li>Unlimited transactions</li>
                <li>Unlimited team members</li>
                <li>
                  Pay by pre-authorized debit or <a
                    href="https://www.bconline.gov.bc.ca/"
                    target="_blank"
                    rel="noopener noreferrer"
                  >BC Online deposit account</a>
                </li>
                <li>Financial Statements</li>
              </ul>
            </div>

            <!-- State Button (Create Account) -->
            <div class="mt-10">
              <v-btn
                large
                block
                depressed
                color="primary"
                class="font-weight-bold"
                data-test="btn-stepper-premium-select"
                :outlined="selectedAccountType != ACCOUNT_TYPE.PREMIUM"
                @click="selectAccountType(ACCOUNT_TYPE.PREMIUM)"
              >
                {{ selectedAccountType == ACCOUNT_TYPE.PREMIUM ? 'SELECTED' : 'SELECT' }}
              </v-btn>
            </div>
          </v-card>
        </v-badge>
      </v-col>
    </v-row>

    <v-divider class="mt-4 mb-10" />

    <v-row>
      <v-col
        cols="12"
        class="form__btns py-0"
      >
        <v-btn
          large
          depressed
          color="default"
          data-test="btn-back"
          @click="goBack"
        >
          <v-icon
            left
            class="mr-2 ml-n2"
          >
            mdi-arrow-left
          </v-icon>
          <span>Back</span>
        </v-btn>
        <v-spacer />
        <v-btn
          large
          color="primary"
          class="mr-3"
          :disabled="!canContinue"
          data-test="btn-stepper-next"
          @click="goNext"
        >
          <span>Next</span>
          <v-icon class="ml-2">
            mdi-arrow-right
          </v-icon>
        </v-btn>
        <ConfirmCancelButton
          :showConfirmPopup="false"
          :target-route="cancelUrl"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { AccessType, Account, LoginSource, SessionStorageKeys } from '@/util/constants'
import { Action, State } from 'pinia-class'
import { Component, Mixins, Prop } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import { Organization } from '@/models/Organization'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

  @Component({
    components: {
      ConfirmCancelButton
    }
  })
export default class AccountTypeSelector extends Mixins(Steppable) {
  private readonly ACCOUNT_TYPE = Account
  private selectedAccountType = ''
  @Prop() cancelUrl: string

  @State(useOrgStore) private isCurrentSelectedProductsPremiumOnly!: boolean
  @State(useOrgStore) private currentOrganization!: Organization
  @State(useOrgStore) private currentOrganizationType!: string
  @State(useOrgStore) private resetAccountTypeOnSetupAccount!: string

  @State(useUserStore) currentUser!: KCUserProfile

  @Action(useOrgStore) setSelectedAccountType!: (selectedAccountType: Account) => void
  @Action(useOrgStore) setCurrentOrganization!: (organization: Organization) => void
  @Action(useOrgStore) setCurrentOrganizationType!: (orgType: string) => void
  @Action(useOrgStore) resetCurrentOrganisation!: () => void
  @Action(useOrgStore) setAccessType!: (accessType: string) => void
  @Action(useOrgStore) setResetAccountTypeOnSetupAccount!: (resetAccountTypeOnSetupAccount: boolean) => void

  private async mounted () {
    // first time to the page , start afresh..this is Create New account flow
    this.setCurrentOrganization({ name: '' })

    // first time stepper hits step 2 after selecting a premium product/service in step 1
    if (!this.currentOrganizationType && this.isCurrentSelectedProductsPremiumOnly) {
      this.selectAccountType(this.ACCOUNT_TYPE.PREMIUM)
    } else {
      // come back to step 2 or after selecting basic products/services in step 1
      this.selectedAccountType = (this.currentOrganizationType === this.ACCOUNT_TYPE.UNLINKED_PREMIUM)
        ? this.ACCOUNT_TYPE.PREMIUM : this.currentOrganizationType
    }
    this.setAccessType(this.getOrgAccessType())
    const accessType = this.getOrgAccessType()
    this.setCurrentOrganization({ ...this.currentOrganization, ...{ accessType: accessType } })
    // remove current account from session storage .Or else permission of old account will be fetched
    ConfigHelper.removeFromSession('CURRENT_ACCOUNT')
  }

  private selectAccountType (accountType) {
    // removed below code for becid re-upload. need to persisit all data in current org
    // to reset any existing details ;user might have went to user profile ;came back and selects another type scenarios

    this.setSelectedAccountType(accountType)
    this.setCurrentOrganizationType(accountType)
    this.selectedAccountType = accountType
  }

  private getOrgAccessType () {
    let isBceidUser = this.currentUser?.loginSource === LoginSource.BCEID
    let isExtraProvice = JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.ExtraProvincialUser || '{}'))
    const isGovNAccount = !!JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.GOVN_USER || 'false'))

    if (isGovNAccount) {
      return AccessType.GOVN
    }
    return isBceidUser ? (isExtraProvice ? AccessType.EXTRA_PROVINCIAL : AccessType.REGULAR_BCEID) : AccessType.REGULAR
  }

  private goNext () {
    this.stepForward(this.selectedAccountType === this.ACCOUNT_TYPE.PREMIUM)
  }

  private goBack () {
    this.stepBack()
  }

  private get canContinue () {
    return this.selectedAccountType
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
  height: 100%;
  //background-color: var(--v-grey-lighten4) !important;

  &:hover {
    border-color: var(--v-primary-base) !important;
  }

  &.active {
    box-shadow: 0 0 0 2px inset var(--v-primary-base),
                0 3px 1px -2px rgba(0,0,0,.2),
                0 2px 2px 0 rgba(0,0,0,.14),
                0 1px 5px 0 rgba(0,0,0,.12) !important;
  }
}

.theme--light.v-card.v-card--outlined.active {
  border-color: var(--v-primary-base);
}

.account-type {
  flex: 1 1 auto;

  &__title {
    margin-top: -0.25rem;
    margin-bottom: 0.15rem;
    line-height: 1.75rem;
    font-size: 1.5rem;
    font-weight: 700;
  }

  &__name {
    margin-bottom: 1.5rem;
    font-weight: 700;
    color: var(--v-grey-darken1);
  }

  &__summary {
    margin-bottom: 2rem;
  }

  &__details {
    margin-bottom: 2.25rem;
    font-size: 0.875rem;
    font-weight: 700;

    li {
      padding-left: 0.75rem;
    }

    li + li {
      margin-top: 0.75rem;
    }
  }
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

.active .selected-icon {
  opacity: 1;
  transform: scale(1);
}

.select-account-btn  {
  width: 20rem;
  font-weight: 700;
}

.premium-badge-chip {
  background: var(--v-secondary-lighten1) !important;
  color: var(--v-accent-lighten5) !important;
  white-space: break-spaces !important;
  width: 250px !important;
  height: auto !important;
  text-align: start;
  padding: 10px;
}

::v-deep .v-badge__wrapper {
  width: 50% !important;
}

::v-deep .v-badge__badge  {
  height: 40px !important;
}

.form__btns {
  display: flex;
  justify-content: flex-end;
}

</style>
