<template>
  <v-container>
    <v-form
      ref="premiumAccountChooser"
      lazy-validation
      data-test="form-premium-account-chooser"
    >
      <!-- v-mode is display-mode -->
      <div v-display-mode>
        <p class="mb-6">
          <span>Do you want to link this account with an existing BC Online Account?</span>
        &nbsp;
          <v-btn
            text
            color="primary"
            class="learn-more-btn"
            data-test="modal-learnmore-dialog"
            @click="learnMoreDialog = true"
          >
            Learn more
          </v-btn>
        </p>
        <v-radio-group
          v-model="isBcolSelected"
          hide-details
          class="mb-9"
          data-test="radio-isBcolSelected"
          @change="loadComponent"
        >
          <v-radio
            label="Yes"
            value="yes"
            data-test="radio-isBcolSelected-yes"
          />
          <v-radio
            label="No"
            value="no"
            data-test="radio-isBcolSelected-no"
          />
        </v-radio-group>
      </div>
      <component
        :is="currentComponent"
        ref="activeComponent"
        class="mt-5 pa-0"
        :step-back="stepBack"
        :step-forward="stepForward"
        :readOnly="readOnly"
      />

      <template v-if="!isBcolSelected">
        <v-divider class="mt-4 mb-10" />
        <v-row>
          <v-col
            cols="12"
            class="form__btns py-0 d-inline-flex"
          >
            <v-btn
              large
              depressed
              color="default"
              data-test="btn-back"
              @click="stepBack"
            >
              <v-icon
                left
                class="mr-2 ml-n2"
              >
                mdi-arrow-left
              </v-icon>
              Back
            </v-btn>
            <v-spacer />
            <v-btn
              class="mr-3"
              large
              depressed
              color="primary"
              :loading="saving"
              :disabled="saving || !isBcolSelected"
              data-test="btn-next"
            >
              <span>Next
                <v-icon
                  right
                  class="ml-1"
                >mdi-arrow-right</v-icon>
              </span>
            </v-btn>
            <ConfirmCancelButton
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
      data-test="modal-learn-more-dialog-content"
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
          <p class="pt-2">
            Linking a BC Online account, requires an existing BC Online account (3-5 days to setup) and the Prime Contact credentials to complete.
          </p>
          <v-btn
            text
            color="primary"
            class="bcol-link px-2"
            href="https://www.bconline.gov.bc.ca/"
            target="_blank"
            rel="noopener noreferrer"
          >
            <v-icon>mdi-help-circle-outline</v-icon>
            <span>How do I get a BC Online Account?</span>
          </v-btn>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
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

import { Component, Mixins, Prop } from 'vue-property-decorator'
import { mapActions, mapState } from 'pinia'
import { Account } from '@/util/constants'
import AccountCreateBasic from '@/components/auth/create-account/AccountCreateBasic.vue'
import AccountCreatePremium from '@/components/auth/create-account/AccountCreatePremium.vue'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import { Organization } from '@/models/Organization'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import { useOrgStore } from '@/store/org'

@Component({
  components: {
    AccountCreateBasic,
    ConfirmCancelButton
  },
  computed: {
    ...mapState(useOrgStore, [
      'currentOrganization',
      'currentOrganizationType'
    ])
  },
  methods: {
    ...mapActions(useOrgStore, [
      'setCurrentOrganizationType',
      'syncMembership',
      'syncOrganization',
      'resetAccountWhileSwitchingPremium'
    ])
  }
})
export default class PremiumChooser extends Mixins(Steppable) {
  @Prop() cancelUrl: string
  @Prop({ default: false }) readOnly: string
  private readonly currentOrganizationType!: string
  private readonly currentOrganization!: Organization
  private isBcolSelected = null
  private currentComponent = null
  private saving = false
  private errorMessage: string = ''
  private readonly setCurrentOrganizationType!: (orgType: string) => void
  private readonly syncOrganization!: (orgId: number) => Promise<Organization>
  private readonly resetAccountWhileSwitchingPremium!: () => void
  private learnMoreDialog: boolean = false

  $refs: {
    activeComponent: AccountCreatePremium | AccountCreateBasic
  }

  private mounted () {
    this.isBcolSelected = this.readOnly ? 'no' : null

    this.isBcolSelected = ((this.currentOrganizationType === Account.PREMIUM) &&
      this.currentOrganization?.bcolAccountDetails) ? 'yes' : this.isBcolSelected
    this.isBcolSelected = ((this.currentOrganizationType === Account.UNLINKED_PREMIUM) &&
      this.currentOrganization?.name) ? 'no' : this.isBcolSelected
    this.loadComponent(false)
  }

  private loadComponent (isReset?) {
    if (isReset) {
      // Reset the data only if the user perform choices from this page.
      this.resetAccountWhileSwitchingPremium()
    }
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
    height: auto !important;
    padding: 0.2rem 0.2rem !important;
    font-size: 1rem !important;
    text-decoration: underline;
  }

  p .learn-more-btn {
    margin-top: -0.25rem;
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
