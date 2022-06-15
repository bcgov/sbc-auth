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
      :isInitialTOSAccepted="readOnly"
      :isInitialAcknowledged="readOnly"
      v-display-mode
    ></PaymentMethods>
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
import { Account, PaymentTypes } from '@/util/constants'
import { Component, Emit, Mixins, Prop } from 'vue-property-decorator'

import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import { Organization } from '@/models/Organization'
import PaymentMethods from '@/components/auth/common/PaymentMethods.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
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

  @OrgModule.State('currentOrganization') private readonly currentOrganization!: Organization
  @OrgModule.State('currentOrganizationType') private readonly currentOrganizationType!: string
  @OrgModule.State('currentOrgPaymentType') private readonly currentOrgPaymentType!: string

  @OrgModule.Mutation('setCurrentOrganizationPaymentType') private setCurrentOrganizationPaymentType!: (paymentType: string) => void

  private selectedPaymentMethod: string = ''
  private isPADValid: boolean = false

  private goBack () {
    this.stepBack()
  }

  private get pageSubTitle () {
    return 'Select the payment method for this account.'
  }

  private get isEnableCreateBtn () {
    return (this.selectedPaymentMethod === PaymentTypes.PAD)
      ? (this.selectedPaymentMethod && this.isPADValid) : !!this.selectedPaymentMethod
  }

  private setSelectedPayment (payment) {
    this.selectedPaymentMethod = payment
    this.setCurrentOrganizationPaymentType(this.selectedPaymentMethod)
  }

  private setPADValid (isValid) {
    this.isPADValid = isValid
  }

  private save () {
    this.setCurrentOrganizationPaymentType(this.selectedPaymentMethod)
    this.createAccount()
  }

  @Emit('final-step-action')
  private createAccount () {
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
