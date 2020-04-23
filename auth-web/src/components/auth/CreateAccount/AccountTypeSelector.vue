<template>
  <v-container>
    <p>There is no cost to create a BC Registries account. You only pay for the services and products you purchase.</p>
    <v-row>
      <v-col
        class="d-flex align-stretch"
        cols="12"
        sm="6"
      >
        <v-card
          class="account-card pa-8"
          flat
          hover
          :outlined="selectedAccountType == ACCOUNT_TYPE.BASIC"
          @click="selectAccountType(ACCOUNT_TYPE.BASIC)"
        >
          <div class="account-type mb-1">Basic</div>
          <div class="account-type-header">I make 10 purchases per month or less</div>
          <ul class="my-6 account-details">
            <li>For users who file on behalf of their own businesses or conduct a limited number of searches</li>
            <li>Credit card payment only</li>
            <li>Up to 10 purchases per month</li>
          </ul>
        </v-card>
      </v-col>
      <v-col
        class="d-flex align-stretch"
        cols="12"
        sm="6"
      >
        <v-card
          class="account-card pa-8"
          flat
          hover
          :outlined="selectedAccountType == ACCOUNT_TYPE.PREMIUM"
          @click="selectAccountType(ACCOUNT_TYPE.PREMIUM)"
        >
          <div class="account-type mb-1">PREMIUM</div>
          <div class="account-type-header">I make more than 10 purchases per month</div>
          <ul class="my-6 account-details">
            <li>For firms and companies who search frequently or file for a large number of businesses</li>
            <li>Uses your BC Online account to pay for products & services</li>
            <li>Unlimited purchases</li>
          </ul>
          <div>
            <strong>
              Please Note: To create a Premium account, you require an existing BC Online account. You must be the Prime Contact to complete this process.
            </strong>
          </div>
          <div class="help-url mt-4 mb-2">
            <v-btn text color="primary" href="https://www.bconline.gov.bc.ca/" target="_blank" rel="noopener noreferrer">
              <v-icon small>mdi-help-circle-outline</v-icon>
              <span>How do I get a BC Online Account?</span>
            </v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>
    <v-row justify="end">
      <v-col
        cols="12"
        class="text-right"
      >
        <v-btn class="mr-3" large color="primary" @click="goNext" :disabled='!selectedAccountType'>
          Next
        </v-btn>
        <v-btn large depressed color="default" @click="cancel">
          Cancel
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
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

.account-card {
  background: $gray1 !important;
  &.theme--light.v-card.v-card--outlined {
    border-width: 3px;
    border-color: $BCgovBlue5;
    padding: 29px !important;
  }
  .account-type {
    font-weight: 600;
    text-transform: uppercase;
    font-size: .925rem;
    color: $gray6;
  }
  .account-type-header {
    font-size: 1.65rem;
    font-weight: 600;
  }
  .account-details {
    padding-left: 18px;
    li {
      margin-bottom: 1.25rem;
    }
  }
  .help-url {
    .v-btn {
      height: auto !important;
      display: inline-block;
      padding: 0rem !important;
      white-space: normal;
      text-align: left;
      font-weight: 700;
      .v-icon {
        margin-top: 0.1rem;
        margin-right: 0.5rem;
      }

      span {
        text-decoration: underline;
      }
    }
  }
}

</style>
