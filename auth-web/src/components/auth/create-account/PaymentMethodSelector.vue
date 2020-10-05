<template>
  <div>
    <p class="mb-8">
      Select the payment method for this account.
    </p>
    <div>
      <v-card
        class="payment-card px-6 py-3 mb-4"
        :class="{'selected': isPaymentSelected(payment)}"
        flat
        :outlined="!isPaymentSelected(payment)"
        v-for="payment in paymentMethods"
        :key="payment.type"
        >
        <v-row class="align-center">
          <v-col cols="9">
            <div class="font-weight-bold mb-1">{{payment.title}}</div>
            <div>{{payment.subtitle}}</div>
          </v-col>
          <v-col class="text-right">
            <v-btn
              depressed
              :outlined="!isPaymentSelected(payment)"
              class="font-weight-bold"
              color="primary"
              width="100"
              @click="selectPayment(payment)"
            >
              {{(isPaymentSelected(payment)) ? 'SELECTED' : 'SELECT'}}
            </v-btn>
          </v-col>
        </v-row>
        <v-expand-transition>
          <div
            class="my-3"
            v-html="payment.description"
            v-if="isPaymentSelected(payment)">
          </div>
        </v-expand-transition>
      </v-card>
    </div>
    <v-divider class="my-10"></v-divider>
     <v-row>
      <v-col class="py-0 d-inline-flex">
        <v-btn
          large
          depressed
          color="default"
          @click="goBack"
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
        >
          Create Account
        </v-btn>
        <ConfirmCancelButton
          showConfirmPopup="true"
        ></ConfirmCancelButton>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'

@Component({
  components: {
    ConfirmCancelButton
  }
})
export default class PaymentMethodSelector extends Mixins(Steppable) {
  private selectedPaymentMethod: string = ''
  private paymentMethods = [
    {
      type: 'creditcard',
      title: 'Credit Card',
      subtitle: 'Pay for transactions individually with your credit card.',
      description: `You don't need to provide any credit card information with your account. Credit card information will be requested when you are ready to complete a transaction.`,
      isSelected: false
    },
    {
      type: 'onlinebanking',
      title: 'Online Banking',
      subtitle: 'Pay for products and services through your financial institutions website.',
      description: `
          <div class="mb-4">
            Instructions to set up your online banking payment solution will be available in the <strong>Payment Methods</strong> section of your account settings once your account has been created.
          </div>
          <div>
            BC Registries and Online Services <strong>must receive payment in full</strong> from your financial institution prior to the release of items purchased through this service. 
            Receipt of an online banking payment generally takes 2 days from when you make the payment with your financial institution.
          <div>`,
      isSelected: false
    }
  ]

  private goBack () {
    this.stepBack()
  }

  private goNext () {
    this.stepForward()
  }

  private selectPayment (payment) {
    this.selectedPaymentMethod = payment.type
  }

  private isPaymentSelected (payment) {
    return (this.selectedPaymentMethod === payment.type)
  }

  private save () {

  }
}
</script>

<style lang="scss" scoped>
@import "$assets/scss/theme.scss";
.payment-card {
  &:hover {
    border-color: var(--v-primary-base) !important;
  }

  &.selected {
    box-shadow: 0 0 0 2px inset var(--v-primary-base), 0 3px 1px -2px rgba(0,0,0,.2),0 2px 2px 0 rgba(0,0,0,.14),0 1px 5px 0 rgba(0,0,0,.12) !important;
  }
}
</style>
