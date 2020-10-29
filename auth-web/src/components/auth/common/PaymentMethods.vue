<template>
  <div>
    <template v-if="!isPADOnly">
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

          <div class="payment-card-contents">
            <div>
              <div class="title font-weight-bold mt-n2 payment-title">{{payment.title}}</div>
              <div>{{payment.subtitle}}</div>
            </div>
            <v-expand-transition>
              <div v-if="isPaymentSelected(payment)">
                <div class="pt-6">
                  <div v-if="(payment.type === paymentTypes.PAD)">
                    <v-divider class="mb-6"></v-divider>
                    <!-- showing PAD form for PAD selection -->
                    <PADInfoForm
                      @is-pre-auth-debit-form-valid="isPADValid"
                      @emit-pre-auth-debit-info="getPADInfo"
                    ></PADInfoForm>
                  </div>
                  <div v-else-if="(payment.type === paymentTypes.BCOL)">
                    <!-- showing BCOL details banner -->
                    <LinkedBCOLBanner
                      :bcolAccountName="currentOrganization.name"
                      :bcolAccountDetails="currentOrganization.bcolAccountDetails"
                    ></LinkedBCOLBanner>
                  </div>
                  <div v-else>
                    <v-divider class="mb-6"></v-divider>
                    <div v-html="payment.description"></div>
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
    </template>
    <!-- showing PAD form without card selector for single payment types -->
    <v-row v-else>
      <v-col cols="9" class="py-0">
        <PADInfoForm
          :padInformation="{}"
          @is-pre-auth-debit-form-valid="isPADValid"
          @emit-pre-auth-debit-info="getPADInfo"
        ></PADInfoForm>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { Account, PaymentTypes } from '@/util/constants'
import { Component, Emit, Mixins, Prop, Vue } from 'vue-property-decorator'
import { Organization, PADInfo } from '@/models/Organization'
import ConfigHelper from '@/util/config-helper'
import LinkedBCOLBanner from '@/components/auth/common/LinkedBCOLBanner.vue'
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
    icon: 'mdi-bank-outline',
    title: 'Pre-authorized Debit',
    subtitle: 'Automatically debit a bank account when payments are due.',
    description: '',
    isSelected: false
  },
  [PaymentTypes.BCOL]: {
    type: PaymentTypes.BCOL,
    icon: 'mdi-link-variant',
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
    PADInfoForm,
    LinkedBCOLBanner
  }
})
export default class PaymentMethodSelector extends Vue {
  @Prop({ default: '' }) currentOrgType: string
  @Prop({ default: undefined }) currentOrganization: Organization
  @Prop({ default: '' }) currentSelectedPaymentMethod: string
  private selectedPaymentMethod: string = ''
  private paymentTypes = PaymentTypes
  private padInfo: PADInfo = {} as PADInfo

  // this object can define the payment methods allowed for each account tyoes
  private paymentsPerAccountType = ConfigHelper.paymentsAllowedPerAccountType()

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

  private get isPADOnly () {
    return (this.currentOrgType === Account.UNLINKED_PREMIUM)
  }

  private mounted () {
    if (!this.isPADOnly) {
      this.selectPayment({ type: this.currentSelectedPaymentMethod })
    }
  }

  private selectPayment (payment) {
    this.selectedPaymentMethod = payment.type
    /**
     * emit the paymentMethodSelected() from here only if its not PAD,
     * for PAD, emit the paymentMethodSelected from the isPADValid method.
     * so that the 'create account' button can be enabled once valid PAD details are entered.
     * also, for single payment options (isPADOnly), this select method wont get fired,
     * so emitting the selection from isPADValid would help there as well.
     * IMP: check for PaymentTypes.PAD instead of 'isPADOnly' here, since that condition can change in future.
     */
    if (payment.type !== PaymentTypes.PAD) {
      this.paymentMethodSelected()
    }
  }

  private isPaymentSelected (payment) {
    return (this.selectedPaymentMethod === payment.type)
  }

  @Emit()
  private paymentMethodSelected () {
    return this.selectedPaymentMethod
  }

  private getPADInfo (padInfo: PADInfo) {
    this.padInfo = padInfo
  }

  private isPADValid (isValid) {
    if (isValid) {
      this.selectedPaymentMethod = PaymentTypes.PAD
      this.paymentMethodSelected()
    }
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

.payment-card-contents {
  width: 100%;
}
</style>
