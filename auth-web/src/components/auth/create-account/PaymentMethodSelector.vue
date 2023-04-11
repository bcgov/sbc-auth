<template>
  <div data-test="div-stepper-payment-method-selector">
    <p class="payment-page-sub mb-9">
      {{pageSubTitle}}
    </p>
    <PaymentMethods
      :currentOrgType="currentOrganizationType"
      :currentOrganization="currentOrganization"
      :currentSelectedPaymentMethod="currentOrgPaymentType"
      @payment-method-selected="setSelectedPayment"
      @is-pad-valid="setPADValid"
      @emit-bcol-info="setBcolInfo"
      :isInitialTOSAccepted="readOnly"
      :isInitialAcknowledged="readOnly"
      v-display-mode
    ></PaymentMethods>
    <v-slide-y-transition>
        <div class="pb-2" v-show="errorMessage">
          <v-alert type="error" icon="mdi-alert-circle-outline" data-test="alert-bcol-error">
            {{errorMessage}}
          </v-alert>
        </div>
    </v-slide-y-transition>
    <v-divider class="my-10"></v-divider>
     <v-row>
      <v-col class="py-0 d-inline-flex">
        <v-btn
          large
          depressed
          color="default"
          @click="goBack"
          data-test="btn-stepper-back"
        >
          <v-icon left class="mr-2">mdi-arrow-left</v-icon>
          <span>Back</span>
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          large
          color="primary"
          class="save-continue-button mr-2 font-weight-bold"
          @click="save"
          data-test="save-button"
          :disabled="!isEnableCreateBtn"
        >
        <!-- need to show submit button on review payment -->
         {{ readOnly ? 'Submit' : 'Create Account'}}
        </v-btn>
        <ConfirmCancelButton
          showConfirmPopup="true"
          v-if="!readOnly"
        ></ConfirmCancelButton>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { BcolAccountDetails, BcolProfile } from '@/models/bcol'
import { PaymentTypes } from '@/util/constants'
import { Component, Emit, Mixins, Prop } from 'vue-property-decorator'

import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import PaymentMethods from '@/components/auth/common/PaymentMethods.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import { Organization } from '@/models/Organization'
import { namespace } from 'vuex-class'

const OrgModule = namespace('org')

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
  @OrgModule.Action('validateBcolAccount')
  private readonly validateBcolAccount!: (bcolProfile: BcolProfile) => Promise<BcolAccountDetails>

  @OrgModule.State('currentOrganization') private readonly currentOrganization!: Organization
  @OrgModule.State('currentOrganizationType') private readonly currentOrganizationType!: string
  @OrgModule.State('currentOrgPaymentType') private readonly currentOrgPaymentType!: string

  @OrgModule.Mutation('setCurrentOrganizationPaymentType') private setCurrentOrganizationPaymentType!: (paymentType: string) => void
  @OrgModule.Mutation('setCurrentOrganizationBcolProfile') private setCurrentOrganizationBcolProfile!: (bcolProfile: BcolProfile) => void

  private selectedPaymentMethod: string = ''
  private isPADValid: boolean = false
  private errorMessage: string = ''

  private mounted () {
    this.selectedPaymentMethod = this.currentOrgPaymentType
  }

  private goBack () {
    this.stepBack()
  }

  private get pageSubTitle () {
    return 'Select the payment method for this account.'
  }

  private get isEnableCreateBtn () {
    if (this.selectedPaymentMethod === PaymentTypes.PAD) {
      return this.isPADValid
    } else if (this.selectedPaymentMethod === PaymentTypes.BCOL) {
      return this.currentOrganization.bcolProfile?.password
    } else {
      return !!this.selectedPaymentMethod
    }
  }

  private setSelectedPayment (payment) {
    this.selectedPaymentMethod = payment
    this.setCurrentOrganizationPaymentType(this.selectedPaymentMethod)
    if (this.selectedPaymentMethod !== PaymentTypes.BCOL) {
      this.errorMessage = ''
    }
  }

  private setPADValid (isValid) {
    this.isPADValid = isValid
  }

  private async save () {
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
  private createAccount () {
  }

  @Emit('emit-bcol-info')
  private setBcolInfo (bcolProfile: BcolProfile) {
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
    box-shadow: 0 0 0 2px inset var(--v-primary-base), 0 3px 1px -2px rgba(0,0,0,.2),0 2px 2px 0 rgba(0,0,0,.14),0 1px 5px 0 rgba(0,0,0,.12) !important;
  }
}

.theme--light.v-card.v-card--outlined.selected {
  border-color: var(--v-primary-base);
}

.transparent-divider {
  border-color: transparent !important;
}
</style>
