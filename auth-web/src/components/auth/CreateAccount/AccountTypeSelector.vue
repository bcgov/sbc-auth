<template>
  <div>
    <p class="mb-7">There is no cost to create a BC Registries account. You only pay for the services and products you purchase.</p>
    <v-row>
      <v-col
        class="d-flex align-stretch"
        sm="6"
      >
        <v-card
          class="account-card pa-9"
          :class="{'active': selectedAccountType == ACCOUNT_TYPE.BASIC}"
          flat
          outlined
          hover
          @click="selectAccountType(ACCOUNT_TYPE.BASIC)"
        >
          <div class="account-type__name mb-2">
            Basic
          </div>
          <div class="account-type__title mb-8">
            I make 10 transactions per month or less
          </div>
          <ul class="account-type__details">
            <li class="mb-6">For users who file on behalf of their own businesses or conduct a limited number of searches</li>
            <li class="mb-6">Credit card payment only</li>
            <li>Up to 10 purchases per month</li>
          </ul>
        </v-card>
      </v-col>
      <v-col
        class="d-flex align-stretch"
        sm="6"
      >
        <v-card
          class="account-card pa-9"
          :class="{'active': selectedAccountType == ACCOUNT_TYPE.PREMIUM}"
          flat
          outlined
          hover
          @click="selectAccountType(ACCOUNT_TYPE.PREMIUM)"
        >
          <div class="account-type__name mb-2">PREMIUM</div>
          <div class="account-type__title mb-8">I make more than 10 transactions per month</div>
          <ul class="account-type__details mb-8">
            <li class="mb-6">For firms and companies who search frequently or file for a large number of businesses</li>
            <li class="mb-6">Uses your BC Online account to pay for products & services</li>
            <li>Unlimited purchases</li>
          </ul>
          <div class="mb-7">
            <strong>
              Please Note: To create a Premium account, you require an existing BC Online account. You must be the Prime Contact to complete this process.
            </strong>
          </div>
          <div>
            <v-btn text color="primary" class="bcol-link px-2" href="https://www.bconline.gov.bc.ca/" target="_blank" rel="noopener noreferrer">
              <v-icon>mdi-help-circle-outline</v-icon>
              <span>How do I get a BC Online Account?</span>
            </v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col
        cols="12"
        class="step-btns mt-8 pb-0 text-right"
      >
        <v-btn large color="primary" class="mr-3" @click="goNext" :disabled='!selectedAccountType'>
          <span>Next</span>
          <v-icon class="ml-2">mdi-arrow-right</v-icon>
        </v-btn>
        <v-btn large color="default" @click="cancel">
          Cancel
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">

import { Component, Mixins, Prop, Vue } from 'vue-property-decorator'
import { Account } from '@/util/constants'
import { Organization } from '@/models/Organization'
import Steppable from '@/components/auth/stepper/Steppable.vue'
import { mapMutations } from 'vuex'

@Component({
  components: {

  },
  methods: {
    ...mapMutations('org', ['setSelectedAccountType', 'setCurrentOrganization'])
  }
})
export default class AccountTypeSelector extends Mixins(Steppable) {
  private readonly ACCOUNT_TYPE = Account
  private selectedAccountType: string = ''
  private readonly setSelectedAccountType!: (selectedAccountType: Account) => void
  private readonly setCurrentOrganization!: (organization: Organization) => void

  private async mounted () {
  }

  private selectAccountType (accountType) {
    this.setSelectedAccountType(accountType)
    this.selectedAccountType = accountType
  }

  private goNext () {
    this.stepForward(this.selectedAccountType === this.ACCOUNT_TYPE.PREMIUM)
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
  border-radius: 6px !important;
  background-color: var(--v-grey-lighten4) !important;

  &.active {
    box-shadow: 0 0 0 3px inset var(--v-primary-base);
    background-color: #ffffff;
  }
}

.theme--light.v-card.v-card--outlined.active {
  border-color: var(--v-primary-base);
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
</style>
