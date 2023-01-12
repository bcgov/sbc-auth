<template>
  <div>
     <template v-if="isPaymentEJV">
      <GLPaymentForm :canSelect="false"></GLPaymentForm>
    </template>
    <template v-else-if="!isPaymentEJV">
      <v-card
        outlined
        :ripple="false"
        hover
        class="payment-card py-8 px-8 mb-4 elevation-1"
        :class="{'selected': isPaymentSelected(payment)}"
        v-for="payment in allowedPaymentMethods"
        :key="payment.type"
        v-can:CHANGE_PAYMENT_METHOD.disable.card
        @click="paymentMethodSelected(payment)"
        :data-test="`div-payment-${payment.type}`"
      >
        <div>
          <header class="d-flex align-center">
            <div class="payment-icon-container mt-n2">
              <v-icon x-large color="primary">{{payment.icon}}</v-icon>
            </div>
            <div class="pr-8">
              <h3 class="title font-weight-bold payment-title mt-n1">{{payment.title}}</h3>
              <div>{{payment.subtitle}}</div>
            </div>
            <v-btn
              large
              depressed
              color="primary"
              width="120"
              class="font-weight-bold ml-auto"
              :outlined="!isPaymentSelected(payment)"
              @click="paymentMethodSelected(payment)"
              :aria-label="'Select' + ' ' + payment.title"
              :data-test="`btn-payment-${payment.type}`"
            >
              <span>{{(isPaymentSelected(payment)) ? 'SELECTED' : 'SELECT'}}</span>
            </v-btn>
          </header>

          <div class="payment-card-contents">
            <v-expand-transition>
              <div v-if="isPaymentSelected(payment)">

                <!-- PAD -->
                <div class="pad-form-container pt-7" v-if="(payment.type === paymentTypes.PAD)">
                  <v-divider class="mb-7"></v-divider>
                  <PADInfoForm
                    @is-pre-auth-debit-form-valid="isPADValid"
                    @emit-pre-auth-debit-info="getPADInfo"
                    :isChangeView="isChangeView"
                    :isAcknowledgeNeeded="isAcknowledgeNeeded"
                    :isInitialAcknowledged="isInitialAcknowledged"
                    :isInitialTOSAccepted="isInitialTOSAccepted"
                    :clearOnEdit="isInitialTOSAccepted"
                  ></PADInfoForm>
                </div>

                <!-- BCOL -->
                <div class="pt-7" v-else-if="(payment.type === paymentTypes.BCOL)">
                  <!-- showing BCOL details banner -->
                  <LinkedBCOLBanner
                    :bcolAccountName="currentOrganization.bcolAccountName"
                    :bcolAccountDetails="currentOrganization.bcolAccountDetails"
                    :show-edit-btn="true"
                    :force-edit-mode="forceEditModeBCOL"
                    @emit-bcol-info="setBcolInfo"
                  ></LinkedBCOLBanner>
                </div>

                <!-- Other Payment Types -->
                <div class="pt-7" v-else>
                  <v-divider class="mb-7"></v-divider>
                  <div v-html="payment.description"></div>
                </div>
              </div>
            </v-expand-transition>
          </div>
        </div>
      </v-card>
    </template>
    <!-- showing PAD form without card selector for single payment types -->
    <v-row v-else>
      <v-col cols="9" class="py-0">
        <PADInfoForm
          :padInformation="{}"
          @is-pre-auth-debit-form-valid="isPADValid($event)"
          @emit-pre-auth-debit-info="getPADInfo($event)"
          :isChangeView="isChangeView"
          :isAcknowledgeNeeded="isAcknowledgeNeeded"
          :isInitialTOSAccepted="isInitialTOSAccepted"
          :isInitialAcknowledged="isInitialAcknowledged"
          :clearOnEdit="isInitialTOSAccepted"
          @is-pad-info-touched="isPadInfoTouched($event)"
        ></PADInfoForm>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { Organization, PADInfo } from '@/models/Organization'
import { BcolProfile } from '@/models/bcol'
import ConfigHelper from '@/util/config-helper'
import GLPaymentForm from '@/components/auth/common/GLPaymentForm.vue'
import LinkedBCOLBanner from '@/components/auth/common/LinkedBCOLBanner.vue'
import PADInfoForm from '@/components/auth/common/PADInfoForm.vue'
import { PaymentTypes } from '@/util/constants'
import { namespace } from 'vuex-class'

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
        <p><strong>Online banking is currently limited to the following institutions:</strong></p>
        <p>
          <ul>
            <li>Bank of Montreal</li>
            <li>Central 1 Credit Union</li>
            <li>Coast Capital Savings</li>
            <li>HSBC</li>
            <li>Royal Bank of Canada (RBC)</li>
            <li>Scotiabank</li>
            <li>TD Canada Trust (TD)</li>
          </ul>
        </p>
        <p>
          Instructions to set up your online banking payment solution will be available in the <strong>Payment Methods</strong> section of your account settings once your account has been created.
        </p>
        <p class="mb-0">
          BC Registries and Online Services <strong>must receive payment in full</strong> from your financial institution prior to the release of items purchased through this service. Receipt of an online banking payment generally takes 3-4 days from when you make the payment with your financial institution.
        </p>`,
    isSelected: false
  }
}

const orgModule = namespace('org')

@Component({
  components: {
    PADInfoForm,
    LinkedBCOLBanner,
    GLPaymentForm
  }
})
export default class PaymentMethods extends Vue {
  @Prop({ default: '' }) currentOrgType: string
  @Prop({ default: undefined }) currentOrganization: Organization
  @Prop({ default: '' }) currentSelectedPaymentMethod: string
  @Prop({ default: undefined }) currentOrgPaymentType: string
  @Prop({ default: false }) isChangeView: boolean
  @Prop({ default: true }) isAcknowledgeNeeded: boolean
  @Prop({ default: false }) isTouchedUpdate: boolean
  @Prop({ default: false }) isInitialTOSAccepted: boolean
  @Prop({ default: false }) isInitialAcknowledged: boolean

  @orgModule.Action('fetchCurrentOrganizationGLInfo') public fetchCurrentOrganizationGLInfo!:(accountId: number) =>Promise<any>

  private selectedPaymentMethod: string = ''
  private paymentTypes = PaymentTypes
  private padInfo: PADInfo = {} as PADInfo
  private isTouched: boolean = false
  private ejvPaymentInformationTitle = 'General Ledger Information'

  // this object can define the payment methods allowed for each account tyoes
  private paymentsPerAccountType = ConfigHelper.paymentsAllowedPerAccountType()

  private get allowedPaymentMethods () {
    const paymentMethods = []
    if (this.currentOrgType) {
      const paymentTypes = this.paymentsPerAccountType[this.currentOrgType]
      paymentTypes.forEach(paymentType => {
        if (PAYMENT_METHODS[paymentType]) {
          paymentMethods.push(PAYMENT_METHODS[paymentType])
        }
      })
    }
    return paymentMethods
  }

  private get forceEditModeBCOL () {
    return this.currentSelectedPaymentMethod === PaymentTypes.BCOL &&
           this.currentOrgPaymentType !== undefined &&
           this.currentOrgPaymentType !== PaymentTypes.BCOL
  }

  private get isPaymentEJV () {
    return this.currentSelectedPaymentMethod === PaymentTypes.EJV
  }

  // set on change of input only for single allowed payments
  private isPadInfoTouched (isTouched: boolean) {
    this.isTouched = isTouched
  }

  private async mounted () {
    this.paymentMethodSelected({ type: this.currentSelectedPaymentMethod }, false)
    if (this.isPaymentEJV) {
      await this.fetchCurrentOrganizationGLInfo(this.currentOrganization?.id)
    }
  }

  private isPaymentSelected (payment) {
    return (this.selectedPaymentMethod === payment.type)
  }

  @Emit()
  private paymentMethodSelected (payment, isTouched = true) {
    this.selectedPaymentMethod = payment.type
    this.isTouched = isTouched
    // emit touched flag for parent element
    if (this.isTouchedUpdate) {
      return { selectedPaymentMethod: this.selectedPaymentMethod, isTouched }
    }
    return this.selectedPaymentMethod
  }

  @Emit('get-PAD-info')
  private getPADInfo (padInfo: PADInfo) {
    this.padInfo = padInfo
    return this.padInfo
  }

  @Emit('emit-bcol-info')
  private setBcolInfo (bcolProfile: BcolProfile) {
    return bcolProfile
  }

  @Emit('is-pad-valid')
  private isPADValid (isValid) {
    if (isValid) {
      this.paymentMethodSelected({ type: PaymentTypes.PAD }, this.isTouched)
    }
    // if !this.isTouched then nothing has changed (keeps save btn disabled)
    return isValid && this.isTouched
  }
}
</script>

<style lang="scss" scoped>
.payment-card {
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

.payment-icon-container {
  flex: 0 0 auto;
  width: 4.5rem;
}

.payment-card-contents {
  padding-left: 4.5rem;
}

.pad-form-container {
  max-width: 75ch;
}
</style>
