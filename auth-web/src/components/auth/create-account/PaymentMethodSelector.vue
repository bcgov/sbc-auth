<template>
  <div data-test="div-stepper-payment-method-selector">
    <p class="payment-page-sub mb-9">
      {{ pageSubTitle }}
    </p>
    <PaymentMethods
      v-display-mode
      :currentOrgType="currentOrganizationType"
      :currentOrganization="currentOrganization"
      :currentSelectedPaymentMethod="currentOrgPaymentType"
      :isInitialTOSAccepted="readOnly"
      :isInitialAcknowledged="readOnly"
      @payment-method-selected="setSelectedPayment"
      @is-pad-valid="setPADValid"
      @emit-bcol-info="setBcolInfo"
    />
    <v-slide-y-transition>
      <div
        v-show="errorMessage"
        class="pb-2"
      >
        <v-alert
          type="error"
          icon="mdi-alert-circle-outline"
          data-test="alert-bcol-error"
        >
          {{ errorMessage }}
        </v-alert>
      </div>
    </v-slide-y-transition>
    <v-divider class="my-10" />
    <v-row>
      <v-col class="py-0 d-inline-flex">
        <v-btn
          large
          depressed
          color="default"
          data-test="btn-stepper-back"
          @click="goBack"
        >
          <v-icon
            left
            class="mr-2"
          >
            mdi-arrow-left
          </v-icon>
          <span>Back</span>
        </v-btn>
        <v-spacer />
        <v-btn
          large
          color="primary"
          class="save-continue-button mr-2 font-weight-bold"
          data-test="save-button"
          :disabled="!isEnableCreateBtn"
          @click="save"
        >
          <!-- need to show submit button on review payment -->
          {{ readOnly ? 'Submit' : 'Create Account' }}
        </v-btn>
        <ConfirmCancelButton
          v-if="!readOnly"
          showConfirmPopup="true"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { Action, State } from 'pinia-class'
import { BcolAccountDetails, BcolProfile } from '@/models/bcol'
import { Component, Emit, Mixins, Prop } from 'vue-property-decorator'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import { Organization } from '@/models/Organization'
import PaymentMethods from '@/components/auth/common/PaymentMethods.vue'
import { PaymentTypes } from '@/util/constants'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import { useOrgStore } from '@/store/org'

@Component({
  components: {
    ConfirmCancelButton,
    PaymentMethods
  }
})
export default class PaymentMethodSelector extends Mixins(Steppable) {
  // need toi show TOS as checked in stepper BCEID re-upload time.
  // show submit button on final stepper to update info, even this page is read only
  @Prop({ default: false }) readOnly: boolean
  @Action(useOrgStore) readonly validateBcolAccount!: (bcolProfile: BcolProfile) => Promise<BcolAccountDetails>

  @State(useOrgStore) readonly currentOrganization!: Organization
  @State(useOrgStore) readonly currentOrganizationType!: string
  @State(useOrgStore) readonly currentOrgPaymentType!: string

  @Action(useOrgStore) setCurrentOrganizationPaymentType!: (paymentType: string) => void
  @Action(useOrgStore) setCurrentOrganizationBcolProfile!: (bcolProfile: BcolProfile) => void

  selectedPaymentMethod: string = ''
  isPADValid: boolean = false
  errorMessage: string = ''

  private mounted () {
    this.selectedPaymentMethod = this.currentOrgPaymentType
  }

  goBack () {
    this.stepBack()
  }

  get pageSubTitle () {
    return 'Select the payment method for this account.'
  }

  get isEnableCreateBtn () {
    if (this.selectedPaymentMethod === PaymentTypes.PAD) {
      return this.isPADValid
    } else if (this.selectedPaymentMethod === PaymentTypes.BCOL) {
      return this.currentOrganization.bcolProfile?.password
    } else {
      return !!this.selectedPaymentMethod
    }
  }

  setSelectedPayment (payment) {
    this.selectedPaymentMethod = payment
    this.setCurrentOrganizationPaymentType(this.selectedPaymentMethod)
    if (this.selectedPaymentMethod !== PaymentTypes.BCOL) {
      this.errorMessage = ''
    }
  }

  setPADValid (isValid) {
    this.isPADValid = isValid
  }

  async save () {
    this.setCurrentOrganizationPaymentType(this.selectedPaymentMethod)
    if (this.selectedPaymentMethod !== PaymentTypes.BCOL) {
      // It's possible this is already set from being linked, so we need to empty it out.
      this.setCurrentOrganizationBcolProfile(null)
      this.createAccount()
      return
    }
    try {
      const bcolAccountDetails = await this.validateBcolAccount(this.currentOrganization.bcolProfile)
      this.errorMessage = bcolAccountDetails ? null : 'Error - No account details provided for this account.'
      this.setCurrentOrganizationBcolProfile(this.currentOrganization.bcolProfile)
    } catch (err) {
      switch (err.response.status) {
        case 409:
          this.errorMessage = err.response.data.message
          break
        case 400:
          this.errorMessage = err.response.data.message
          break
        default:
          this.errorMessage = 'An error occurred while attempting to create your account.'
      }
    }
    if (!this.errorMessage) {
      this.createAccount()
    }
  }

  @Emit('final-step-action')
  createAccount () {
  }

  @Emit('emit-bcol-info')
  setBcolInfo (bcolProfile: BcolProfile) {
    this.setCurrentOrganizationBcolProfile(bcolProfile)
  }
}
</script>

<style lang="scss" scoped>
.payment-card {
  background-color: var(--v-grey-lighten5) !important;
  transition: all ease-out 0.2s;

  &:hover {
    border-color: var(--v-primary-base) !important;
  }

  &.selected {
    box-shadow: 0 0 0 2px inset var(--v-primary-base),
                0 3px 1px -2px rgba(0,0,0,.2),
                0 2px 2px 0 rgba(0,0,0,.14),
                0 1px 5px 0 rgba(0,0,0,.12) !important;
  }
}

.theme--light.v-card.v-card--outlined.selected {
  border-color: var(--v-primary-base);
}

.transparent-divider {
  border-color: transparent !important;
}
</style>
