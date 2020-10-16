<template>
  <div>
    <v-card
      outlined
      hover
      class="payment-card py-8 px-8 mb-4 elevation-1"
      :class="{'selected': isPaymentSelected(payment)}"
      v-for="payment in allowedPaymentMethods"
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
                <div v-if="(payment.type === paymentTypes.PAD)">
                  <!-- showing PAD form for PAD selection -->
                  <PADInfoForm
                    :padInformation="{}"
                    @emit-pre-auth-debit-info="getPADInfo"
                  ></PADInfoForm>
                </div>
                <div v-else
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
</template>

<script lang="ts">
import { Account, PaymentTypes } from '@/util/constants'
import { Component, Emit, Mixins, Prop, Vue } from 'vue-property-decorator'
import PADInfoForm from '@/components/auth/common/PADInfoForm.vue'

const PAYMENT_METHODS = {
  [PaymentTypes.CREDIT_CARD]: {
    type: PaymentTypes.CREDIT_CARD,
    icon: 'mdi-credit-card-outline',
    title: 'Credit Card',
    subtitle: 'Pay for transactions individually with your credit card.',
    description: `You don't need to provide any credit card information with your account. Credit card information will be requested when you are ready to complete a transaction.`,
    isSelected: false
  },
  [PaymentTypes.PAD]: {
    type: PaymentTypes.PAD,
    icon: 'mdi-credit-card-outline',
    title: 'Pre-authorized Debit',
    subtitle: 'Automatically debit a bank account when payments are due.',
    description: '',
    isSelected: false
  },
  [PaymentTypes.BCOL]: {
    type: PaymentTypes.BCOL,
    icon: 'mdi-credit-card-outline',
    title: 'BC Online',
    subtitle: 'Use your linked BC Online account for payment.',
    description: '',
    isSelected: false
  },
  [PaymentTypes.ONLINE_BANKING]: {
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
}

@Component({
  components: {
    PADInfoForm
  }
})
export default class PaymentMethodSelector extends Vue {
  @Prop({ default: '' }) currentOrgType: string
  private selectedPaymentMethod: string = ''
  private paymentTypes = PaymentTypes
  private paymentsPerAccountType = {
    [Account.BASIC]: [ PaymentTypes.CREDIT_CARD, PaymentTypes.ONLINE_BANKING ],
    [Account.PREMIUM]: [ PaymentTypes.PAD, PaymentTypes.BCOL ],
    [Account.UNLINKED_PREMIUM]: [ PaymentTypes.PAD ]
  }

  private get allowedPaymentMethods () {
    const paymentMethods = []
    if (this.currentOrgType) {
      const paymentTypes = this.paymentsPerAccountType[this.currentOrgType]
      paymentTypes.forEach(paymentType => {
        paymentMethods.push(PAYMENT_METHODS[paymentType])
      })
    }
    return paymentMethods
  }

  private selectPayment (payment) {
    this.selectedPaymentMethod = payment.type
    this.paymentMethodSelected()
  }

  private isPaymentSelected (payment) {
    return (this.selectedPaymentMethod === payment.type)
  }

  @Emit()
  private paymentMethodSelected () {
    return this.selectedPaymentMethod
  }

  private getPADInfo (padInfo) {
    // eslint-disable-next-line no-console
    console.log(padInfo)
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
