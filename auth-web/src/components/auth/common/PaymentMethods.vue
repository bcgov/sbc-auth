<template>
  <div>
    <template v-if="isPaymentEJV">
      <GLPaymentForm :canSelect="false" />
    </template>
    <template v-else-if="!isPaymentEJV">
      <v-card
        v-for="payment in allowedPaymentMethods"
        :key="payment.type"
        v-can:CHANGE_PAYMENT_METHOD.disable.card
        outlined
        :ripple="false"
        hover
        class="payment-card py-8 px-8 mb-4 elevation-1"
        :class="{'selected': isPaymentSelected(payment)}"
        :data-test="`div-payment-${payment.type}`"
        @click="paymentMethodSelected(payment)"
      >
        <div>
          <header class="d-flex align-center">
            <div class="payment-icon-container mt-n2">
              <v-icon
                x-large
                color="primary"
              >
                {{ payment.icon }}
              </v-icon>
            </div>
            <div class="pr-8">
              <h3 class="title font-weight-bold payment-title mt-n1">
                {{ payment.title }}
              </h3>
              <div>{{ payment.subtitle }}</div>
            </div>
            <v-btn
              large
              depressed
              color="primary"
              width="120"
              class="font-weight-bold ml-auto"
              :outlined="!isPaymentSelected(payment)"
              :aria-label="'Select' + ' ' + payment.title"
              :data-test="`btn-payment-${payment.type}`"
              @click="paymentMethodSelected(payment)"
            >
              <span>{{ (isPaymentSelected(payment)) ? 'SELECTED' : 'SELECT' }}</span>
            </v-btn>
          </header>

          <div class="payment-card-contents">
            <v-expand-transition>
              <div v-if="isPaymentSelected(payment)">
                <!-- PAD -->
                <div
                  v-if="(payment.type === paymentTypes.PAD)"
                  class="pad-form-container pt-7"
                >
                  <v-divider class="mb-7" />
                  <PADInfoForm
                    :isChangeView="isChangeView"
                    :isAcknowledgeNeeded="isAcknowledgeNeeded"
                    :isInitialAcknowledged="isInitialAcknowledged"
                    :isInitialTOSAccepted="isInitialTOSAccepted"
                    :clearOnEdit="isInitialTOSAccepted"
                    @is-pre-auth-debit-form-valid="isPADValid"
                    @emit-pre-auth-debit-info="getPADInfo"
                  />
                </div>

                <!-- BCOL -->
                <div
                  v-else-if="(payment.type === paymentTypes.BCOL)"
                  class="pt-7"
                >
                  <!-- showing BCOL details banner -->
                  <LinkedBCOLBanner
                    :bcolAccountName="currentOrganization.bcolAccountName"
                    :bcolAccountDetails="currentOrganization.bcolAccountDetails"
                    :show-edit-btn="true"
                    :force-edit-mode="forceEditModeBCOL"
                    @emit-bcol-info="setBcolInfo"
                  />
                </div>

                <!-- EFT -->
                <div
                  v-else-if="(payment.type === paymentTypes.EFT)"
                  class="pt-7"
                >
                  <v-divider class="mb-7" />
                  <div class="mb-7">
                    To send us a payment through electronic funds transfer (EFT), please read the
                    <a @click="getEftInstructions">Electronic Funds Transfer Payment Instructions</a>.
                  </div>
                  <div class="terms-container">
                    <TermsOfUseDialog
                      :isAlreadyAccepted="isEFTTOSAccepted"
                      :tosText="'Terms and Conditions of the Electronic Funds Transfer'"
                      :tosType="'termsofuse_pad'"
                      :tosHeading="'Electronic Funds Transfer Terms and Conditions Agreement, BC Registry and Online Services'"
                      :tosCheckBoxLabelAppend="'for BC Registry Services'"
                      @terms-acceptance-status="updateEFTTermsAccepted($event)"
                    />
                  </div>
                </div>

                <!-- Other Payment Types -->
                <div
                  v-else
                  class="pt-7"
                >
                  <v-divider class="mb-7" />
                  <div v-html="payment.description" />
                </div>
              </div>
            </v-expand-transition>
          </div>
        </div>
      </v-card>
    </template>
    <!-- showing PAD form without card selector for single payment types -->
    <v-row v-else>
      <v-col
        cols="9"
        class="py-0"
      >
        <PADInfoForm
          :padInformation="{}"
          :isChangeView="isChangeView"
          :isAcknowledgeNeeded="isAcknowledgeNeeded"
          :isInitialTOSAccepted="isInitialTOSAccepted"
          :isInitialAcknowledged="isInitialAcknowledged"
          :clearOnEdit="isInitialTOSAccepted"
          @is-pre-auth-debit-form-valid="isPADValid($event)"
          @emit-pre-auth-debit-info="getPADInfo($event)"
          @is-pad-info-touched="isPadInfoTouched($event)"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, ref } from '@vue/composition-api'
import { BcolProfile } from '@/models/bcol'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import DocumentService from '@/services/document.services'
import GLPaymentForm from '@/components/auth/common/GLPaymentForm.vue'
import LinkedBCOLBanner from '@/components/auth/common/LinkedBCOLBanner.vue'
import PADInfoForm from '@/components/auth/common/PADInfoForm.vue'
import TermsOfUseDialog from '@/components/auth/common/TermsOfUseDialog.vue'
import { PaymentTypes } from '@/util/constants'
import { useOrgStore } from '@/stores/org'

const PAYMENT_METHODS = {
  [PaymentTypes.CREDIT_CARD]: {
    type: PaymentTypes.CREDIT_CARD,
    icon: 'mdi-credit-card-outline',
    title: 'Credit Card',
    subtitle: 'Pay for transactions individually with your credit card.',
    description: `You don't need to provide any credit card information with your account. Credit card information will
                  be requested when you are ready to complete a transaction.`,
    isSelected: false
  },
  [PaymentTypes.EFT]: {
    type: PaymentTypes.EFT,
    icon: 'mdi-arrow-right-circle-outline',
    title: 'Electronic Funds Transfer',
    subtitle: 'Make payments from your bank account. Statement will be issued monthly.',
    description: ``,
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
          Once your account is created, you can use your account number to add BC Registries and Online Services as a
          payee in your financial institution's online banking system to make payments.
        </p>
        <p class="mb-0">
          BC Registries and Online Services <strong>must receive payment in full</strong> 
          from your financial institution prior to the release of items purchased through this service. 
          Receipt of an online banking payment generally takes 3-4 days from when you make the payment with your 
          financial institution.
        </p>`,
    isSelected: false
  }
}

export default defineComponent({
  name: 'PaymentMethods',
  components: {
    PADInfoForm,
    LinkedBCOLBanner,
    GLPaymentForm,
    TermsOfUseDialog
  },
  props: {
    currentOrgType: { default: '' },
    currentOrganization: { default: undefined },
    currentSelectedPaymentMethod: { default: '' },
    currentOrgPaymentType: { default: undefined },
    isChangeView: { default: false },
    isAcknowledgeNeeded: { default: true },
    isTouchedUpdate: { default: false },
    isInitialTOSAccepted: { default: false },
    isInitialAcknowledged: { default: false }
  },
  emits: ['get-PAD-info', 'emit-bcol-info', 'is-pad-valid', 'is-eft-valid', 'payment-method-selected'],
  setup (props, { emit }) {
    const { fetchCurrentOrganizationGLInfo, currentOrgPaymentDetails } = useOrgStore()

    const selectedPaymentMethod = ref('')
    const paymentTypes = PaymentTypes
    const padInfo = ref({})
    const isTouched = ref(false)
    const ejvPaymentInformationTitle = 'General Ledger Information'
    const isEFTTOSAccepted = ref(false)

    // this object can define the payment methods allowed for each account tyoes
    const paymentsPerAccountType = ConfigHelper.paymentsAllowedPerAccountType()

    const allowedPaymentMethods = computed(() => {
      const paymentMethods = []
      if (props.currentOrgType) {
        const paymentTypes = paymentsPerAccountType[props.currentOrgType]
        paymentTypes.forEach((paymentType) => {
          if (PAYMENT_METHODS[paymentType]) {
            paymentMethods.push(PAYMENT_METHODS[paymentType])
          }
        })
      }
      if (currentOrgPaymentDetails?.eftEnable) {
        paymentMethods.push(PAYMENT_METHODS[PaymentTypes.EFT])
      }
      return paymentMethods
    })

    const forceEditModeBCOL = computed(() =>
      props.currentSelectedPaymentMethod === PaymentTypes.BCOL &&
      props.currentOrgPaymentType !== undefined &&
      props.currentOrgPaymentType !== PaymentTypes.BCOL
    )

    const isPaymentEJV = computed(() => selectedPaymentMethod.value === PaymentTypes.EJV)

    // set on change of input only for single allowed payments
    const isPadInfoTouched = (isTouch: boolean) => {
      isTouched.value = isTouch
    }

    const isPaymentSelected = (payment) => {
      return (selectedPaymentMethod.value === payment.type)
    }

    const getEftInstructions = async () => {
      try {
        const downloadData = await DocumentService.getEftInstructions()
        CommonUtils.fileDownload(downloadData?.data, `bcrs_eft_instructions.pdf`, downloadData?.headers['content-type'])
      } catch (error) {
        // eslint-disable-next-line no-console
        console.log(error)
      }
    }

    const paymentMethodSelected = (payment, isTouch = true) => {
      selectedPaymentMethod.value = payment.type
      isTouched.value = isTouch
      // Emit touched flag for the parent element
      if (props.isTouchedUpdate) {
        emit('payment-method-selected', { selectedPaymentMethod: selectedPaymentMethod.value, isTouched: isTouched.value })
      } else {
        emit('payment-method-selected', selectedPaymentMethod.value)
      }
    }

    const getPADInfo = (padInfoValue) => {
      padInfo.value = padInfoValue
      emit('get-PAD-info', padInfoValue)
    }

    const setBcolInfo = (bcolProfile: BcolProfile) => {
      emit('emit-bcol-info', bcolProfile)
    }

    const isPADValid = (isValid) => {
      if (isValid) {
        paymentMethodSelected({ type: PaymentTypes.PAD }, isTouched.value)
      }
      emit('is-pad-valid', isValid && isTouched.value)
    }

    const updateEFTTermsAccepted = (isAccepted: boolean) => {
      isEFTTOSAccepted.value = isAccepted
      isTouched.value = true
      emit('is-eft-valid', isAccepted && isTouched.value)
    }

    onMounted(async () => {
      paymentMethodSelected({ type: props.currentSelectedPaymentMethod }, false)
      if (isPaymentEJV.value) {
        await fetchCurrentOrganizationGLInfo(props.currentOrganization?.id)
      }
    })

    return {
      selectedPaymentMethod,
      paymentTypes,
      padInfo,
      isTouched,
      ejvPaymentInformationTitle,
      allowedPaymentMethods,
      forceEditModeBCOL,
      isPaymentEJV,
      getEftInstructions,
      paymentMethodSelected,
      getPADInfo,
      setBcolInfo,
      isPADValid,
      isPadInfoTouched,
      isPaymentSelected,
      updateEFTTermsAccepted,
      isEFTTOSAccepted
    }
  }
})
</script>

<style lang="scss" scoped>
.payment-card {
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
