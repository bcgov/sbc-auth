<template>
  <div>
    <p class="mb-10">
      Select the payment method for this account.
    </p>
    <div>
      <v-card
        flat
        outlined
        hover
        class="payment-card py-8 px-8 mb-4"
        :class="{'selected': isPaymentSelected(payment)}"
        v-for="payment in paymentMethods"
        :key="payment.type"
        @click="selectPayment(payment)"
      >
        <div class="d-flex">
          <div class="flex--grow">
            <div class="title font-weight-bold mt-n2 payment-title">{{payment.title}}</div>
            <div>{{payment.subtitle}}</div>
          </div>
          <v-btn
            large
            depressed
            color="primary"
            width="120"
            class="font-weight-bold ml-auto"
            :outlined="!isPaymentSelected(payment)"
            @click="selectPayment(payment)"
          >
            {{(isPaymentSelected(payment)) ? 'SELECTED' : 'SELECT'}}
          </v-btn>
        </div>
        <div>
          <v-expand-transition>
            <div v-if="isPaymentSelected(payment)">
              <v-divider class="transparent-divider mb-4"></v-divider>
              <div
                v-html="payment.description">
              </div>
            </div>
          </v-expand-transition>
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
      title: 'Credit Card',
      subtitle: 'Pay for transactions individually with your credit card.',
      description: `You don't need to provide any credit card information with your account. Credit card information will be requested when you are ready to complete a transaction.`,
      isSelected: false
    },
    {
      type: PaymentTypes.ONLINE_BANKING,
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
