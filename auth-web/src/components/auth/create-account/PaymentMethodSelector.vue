<template>
  <div>
    <p class="mb-12">
      Select the payment method for this account.
    </p>
    <div>
      <v-card
        outlined
        hover
        class="payment-card py-8 px-8 mb-4 elevation-1"
        :class="{'selected': isPaymentSelected(payment)}"
        v-for="payment in paymentMethods"
        :key="payment.type"
        @click="selectPayment(payment)"
      >
        <div class="d-flex">
          <div class="mt-n2 mr-8">
            <v-icon x-large color="primary">{{payment.icon}}</v-icon>
          </div>

          <div>
            <div>
              <div class="title font-weight-bold mt-n2 payment-title">{{payment.title}}</div>
              <div>{{payment.subtitle}}</div>
            </div>
            <v-expand-transition>
              <div v-if="isPaymentSelected(payment)">
                <div class="pt-6">
                  <v-divider class="mb-6"></v-divider>
                  <div
                    v-html="payment.description">
                  </div>
                </div>
              </div>
            </v-expand-transition>
          </div>

          <div class="ml-auto pl-8">
          <v-btn
            depressed
            color="primary"
            width="120"
            class="font-weight-bold"
            :outlined="!isPaymentSelected(payment)"
            @click="selectPayment(payment)"
            :aria-label="'Select' + ' ' + payment.title"
          >
            <span>{{(isPaymentSelected(payment)) ? 'SELECTED' : 'SELECT'}}</span>
          </v-btn>
          </div>

        </div>
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
          :disabled="!selectedPaymentMethod"
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
import { Component, Emit, Mixins, Prop } from 'vue-property-decorator'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import OrgModule from '@/store/modules/org'
import { PaymentTypes } from '@/util/constants'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import { mapMutations } from 'vuex'

@Component({
  components: {
    ConfirmCancelButton
  },
  methods: {
    ...mapMutations('org', [
      'setCurrentOrganizationPaymentType'
    ])
  }
})
export default class PaymentMethodSelector extends Mixins(Steppable) {
  private readonly setCurrentOrganizationPaymentType!: (paymentType: string) => void
  private selectedPaymentMethod: string = ''
  private paymentMethods = [
    {
      type: PaymentTypes.CREDIT_CARD,
      icon: 'mdi-credit-card-outline',
      title: 'Credit Card',
      subtitle: 'Pay for transactions individually with your credit card.',
      description: `You don't need to provide any credit card information with your account. Credit card information will be requested when you are ready to complete a transaction.`,
      isSelected: false
    },
    {
      type: PaymentTypes.ONLINE_BANKING,
      icon: 'mdi-bank-outline',
      title: 'Online Banking',
      subtitle: 'Pay for products and services through your financial institutions website.',
      description: `
          <p>
            Instructions to set up your online banking payment solution will be available in the <strong>Payment Methods</strong> section of your account settings once your account has been created.
          </p>
          <p class="mb-0">
            BC Registries and Online Services <strong>must receive payment in full</strong> from your financial institution prior to the release of items purchased through this service. Receipt of an online banking payment generally takes 3-4 days from when you make the payment with your financial institution.
          </p>`,
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
