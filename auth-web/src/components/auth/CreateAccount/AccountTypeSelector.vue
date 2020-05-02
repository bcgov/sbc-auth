<template>
  <div>
    <p class="mb-7">There is no cost to create a BC Registries account. You only pay for the services and products you purchase.</p>
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
            <div class="account-type__name mb-2">
              Basic
            </div>
            <div class="account-type__title mb-8">
              I make 10 transactions per month or less
            </div>
            <ul class="account-type__details">
              <li class="mb-5">For users who file on behalf of their own businesses or conduct a limited number of searches</li>
              <li class="mb-5">Credit card payment only</li>
              <li>Up to 10 purchases per month</li>
            </ul>
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
            <div class="account-type__name mb-2">PREMIUM</div>
            <div class="account-type__title mb-8">I make more than 10 transactions per month</div>
            <ul class="account-type__details mb-8">
              <li class="mb-5">For firms and companies who search frequently or file for a large number of businesses</li>
              <li class="mb-5">Uses your BC Online account to pay for products & services</li>
              <li>Unlimited purchases</li>
            </ul>
            <div class="mb-5">
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
        <ConfirmCancelButton
          :showConfirmPopup="false"
        ></ConfirmCancelButton>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">

import { Component, Mixins, Prop, Vue } from 'vue-property-decorator'
import { mapMutations, mapState } from 'vuex'
import { Account } from '@/util/constants'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import { Organization } from '@/models/Organization'
import Steppable from '@/components/auth/stepper/Steppable.vue'

@Component({
  components: {
    ConfirmCancelButton
  },
  computed: {
    ...mapState('org', ['currentOrganization'])
  },
  methods: {
    ...mapMutations('org', ['setSelectedAccountType', 'setCurrentOrganization', 'resetCurrentOrganisation'])
  }
})
export default class AccountTypeSelector extends Mixins(Steppable) {
  private readonly ACCOUNT_TYPE = Account
  private selectedAccountType: string = ''
  private readonly setSelectedAccountType!: (selectedAccountType: Account) => void
  private readonly setCurrentOrganization!: (organization: Organization) => void
  private readonly currentOrganization!: Organization
  private readonly resetCurrentOrganisation!: () => void

  private async mounted () {
    // first time to the page , start afresh
    if (!this.currentOrganization) {
      this.setCurrentOrganization({ name: '' }) // TODO find a better logic to reset ;may be in cancel button
    } else {
      this.selectedAccountType = this.currentOrganization.orgType
    }
  }

  private selectAccountType (accountType) {
    this.setSelectedAccountType(accountType)
    this.selectedAccountType = accountType
    // to reset any existing details ;user might have went to user profile ;came back and selects another type scenarios
    this.resetCurrentOrganisation()
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
  position: relative;
  background-color: var(--v-grey-lighten4) !important;
  flex-direction: column;

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
