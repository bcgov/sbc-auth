<template>
<v-container>
  <v-form ref="premiumAccountChooser" lazy-validation>
    <p class="mt-3">Do you want to link this account with an existing BC Online Account?
      <v-btn
        text
        class="learn-more-btn"
        color="primary"
        @click="learnMoreDialog = true">Learn more</v-btn>
    </p>
    <v-radio-group class="mb-3" @change="loadComponent" v-model="isBcolSelected">
      <v-radio label="Yes" value="yes" />
      <v-radio label="No" value="no" />
    </v-radio-group>
    <v-divider />
    <component
      ref="activeComponent"
      class="pl-0"
      :is="currentComponent"
      :step-back="stepBack"
      :step-forward="stepForward"
    />
    <template v-if="!isBcolSelected">
      <v-divider />
      <v-row class="my-5">
        <v-col cols="12" class="form__btns py-0 d-inline-flex">
          <v-btn
            large
            depressed
            color="default"
            @click="stepBack">
            <v-icon left class="mr-2 ml-n2">mdi-arrow-left</v-icon>
            Back
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn class="mr-3" large depressed color="primary" :loading="saving" :disabled="saving || !isBcolSelected">
            <span v-if="!isAccountChange">Next
              <v-icon right class="ml-1">mdi-arrow-right</v-icon>
            </span>
            <span v-if="isAccountChange">Change Account</span>

          </v-btn>
          <ConfirmCancelButton
            :clear-current-org="!isAccountChange"
            :target-route="cancelUrl"
          />
        </v-col>
      </v-row>
    </template>
  </v-form>
  <!-- Learn More Popup -->
  <v-dialog
    v-model="learnMoreDialog"
    max-width="500"
  >
    <v-card>
      <v-card-title class="headline">
        <h2>Linking your BC Online account</h2>
        <v-btn
          large
          icon
          @click="closeLearnMore"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text>
        <p>
          When you link your BC Online, you get:
        </p>
        <ul>
          <li>
            <strong>Contact Info</strong> - reuse your account contact information from BC Online for your new premium account
          </li>
          <li>
            <strong>Payment</strong> - the option to select your BC Online deposit account as a payment option
          </li>
          <li>
            <strong>Reporting</strong> - all transactions done by your team in this new application will appear in your BC Online statement reports, provided you choose your BC Online deposit account as your payment option
          </li>
        </ul>
        <p>
          You do not get:
        </p>
        <ul>
          <li>
            To migrate over your userIDs from BC Online
          </li>
        </ul>
        <p class="pt-2">Linking a BC Online account, requires an existing BC Online account (3-5 days to setup) and the Prime Contact credentials to complete.</p>
        <v-btn text color="primary" class="bcol-link px-2" href="https://www.bconline.gov.bc.ca/" target="_blank" rel="noopener noreferrer">
          <v-icon>mdi-help-circle-outline</v-icon>
          <span>How do I get a BC Online Account?</span>
        </v-btn>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          color="default"
          depressed
          @click="closeLearnMore"
        >
          OK
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</v-container>
</template>

<script lang="ts">

import { Account, Actions } from '@/util/constants'
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { mapActions, mapMutations, mapState } from 'vuex'
import AccountCreateBasic from '@/components/auth/create-account/AccountCreateBasic.vue'
import AccountCreatePremium from '@/components/auth/create-account/AccountCreatePremium.vue'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import { Organization } from '@/models/Organization'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import UserProfileForm from '@/components/auth/create-account/UserProfileForm.vue'
import Vue from 'vue'

@Component({
  components: {
    AccountCreateBasic,
    ConfirmCancelButton
  },
  computed: {
    ...mapState('org', [
      'currentOrganization',
      'currentOrganizationType'
    ])
  },
  methods: {
    ...mapMutations('org', [
      'setCurrentOrganizationType'
    ]),
    ...mapActions('org', [
      'createOrg',
      'syncMembership',
      'syncOrganization',
      'changeOrgType'
    ])
  }
})
export default class PremiumChooser extends Mixins(Steppable) {
  @Prop() isAccountChange: boolean
  @Prop() cancelUrl: string
  private readonly currentOrganizationType!: string
  private readonly currentOrganization!: Organization
  private isBcolSelected = null
  private currentComponent = null
  private saving = false
  private errorMessage: string = ''
  private readonly setCurrentOrganizationType!: (orgType: string) => void
  private readonly changeOrgType!: (action: Actions) => Promise<Organization>
  private readonly syncOrganization!: (orgId: number) => Promise<Organization>
  private learnMoreDialog: boolean = false

  $refs: {
    activeComponent: AccountCreatePremium | AccountCreateBasic
  }

  private mounted () {
    if (!this.isAccountChange) {
      this.isBcolSelected = ((this.currentOrganizationType === Account.PREMIUM) && this.currentOrganization?.bcolProfile) ? 'yes' : null
      this.isBcolSelected = (this.currentOrganizationType === Account.UNLINKED_PREMIUM && this.currentOrganization?.name) ? 'no' : this.isBcolSelected
      this.loadComponent()
    }
  }

  private loadComponent () {
    if (this.isBcolSelected === 'yes') {
      this.setCurrentOrganizationType(Account.PREMIUM)
      this.currentComponent = AccountCreatePremium
    } else if (this.isBcolSelected === 'no') {
      this.setCurrentOrganizationType(Account.UNLINKED_PREMIUM)
      this.currentComponent = AccountCreateBasic
    } else {
      this.currentComponent = null
    }
  }

  private cancel () {
    if (this.stepBack) {
      this.stepBack()
    } else {
      this.$router.push({ path: '/home' })
    }
  }

  private closeLearnMore () {
    this.learnMoreDialog = false
  }
}
</script>

<style lang="scss" scoped>
.learn-more-btn {
  padding-left: 0 !important;
  text-decoration: underline !important;
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
  margin-bottom: 16px;
}

ul li::before {
  content: "\2022";  /* Add content: \2022 is the CSS Code/unicode for a bullet */
  color: var(--v-primary-base);
  font-weight: 700;
  display: inline-block;
  width: 1.5rem;
  margin-left: -1.5rem;
}
</style>
